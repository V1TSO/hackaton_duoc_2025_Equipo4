from openai import OpenAI
from app.core.config import settings
from app.agents.rag_service import buscar_en_kb
from app.schemas.analisis_schema import AnalisisEntrada, PrediccionResultado
from app.utils.token_counter import count_tokens, estimate_cost
import logging
import requests

logger = logging.getLogger(__name__)

# Initialize Groq client
groq_api_key = getattr(settings, 'GROQ_API_KEY', None)

# Create OpenAI-compatible client for Groq
client = None
if groq_api_key:
    client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )
else:
    logger.warning("Groq API key not configured. Chat features will be disabled.")

def retrieve_context_from_kb(message: str, top_k: int = 2) -> str:
    """
    Retrieves context from the knowledge base based on the user's message.
    """
    keywords_map = {
        "imc": ["peso", "obesidad", "imc", "sobrepeso", "kilos"],
        "cintura": ["cintura", "abdomen", "barriga", "perímetro"],
        "tabaquismo": ["fumar", "cigarro", "tabaco", "fumar"],
        "actividad_fisica": ["ejercicio", "actividad", "deporte", "caminar", "correr"],
        "sueño": ["dormir", "sueño", "descanso", "insomnio"]
    }
    
    message_lower = message.lower()
    matched_terms = []
    
    for term, keywords in keywords_map.items():
        if any(keyword in message_lower for keyword in keywords):
            matched_terms.append(term)
    
    if not matched_terms:
        matched_terms = ["default"]
    
    logger.info(f"Extracting KB context for terms: {matched_terms}")
    
    try:
        context_json, citations = buscar_en_kb(matched_terms, max_tokens=800)
        return context_json
    except Exception as e:
        logger.error(f"Error retrieving KB context: {e}")
        raise Exception(f"Error al recuperar contexto de la base de conocimiento: {e}")

def generar_plan_con_rag(
    prediccion: PrediccionResultado, 
    datos: AnalisisEntrada
) -> tuple[str, list[str]]:
    
    if client is None:
        logger.error("Groq client not initialized. Cannot generate plan.")
        raise Exception("El servicio de recomendaciones no está disponible. Configure GROQ_API_KEY para habilitar esta función.")
    
    logger.info(f"Generando plan RAG (Groq) para riesgo: {prediccion.categoria_riesgo}")
    
    # Extract feature names from driver objects for KB search
    driver_features = [d.feature if hasattr(d, 'feature') else str(d) for d in prediccion.drivers]
    
    try:
        contexto_rag, citas_kb = buscar_en_kb(driver_features)
    except Exception as e:
        logger.error(f"Fallo en 'buscar_en_kb': {e}")
        raise Exception(f"Error al buscar en la base de conocimiento: {e}") 

    system_prompt = """Eres un coach de bienestar preventivo de CardioSense.
NO eres médico. NO entregas diagnósticos ni tratamientos.
Tu objetivo es generar un plan de acción basado *exclusivamente* en el contexto de la base de conocimiento (KB) proporcionada, la cual está en formato JSON.
Debes citar tus fuentes usando el campo "cita" del JSON, en el formato [Cita: nombre_cita] al final de cada recomendación.
NO puedes alucinar información ni inventar fuentes.
Tu respuesta debe ser un plan de acción breve (3-4 recomendaciones), motivador y en español."""

    altura = f"{datos.altura_cm}cm" if datos.altura_cm is not None else "no disponible"
    peso = f"{datos.peso_kg}kg" if datos.peso_kg is not None else "no disponible"
    presion = f"{datos.presion_sistolica}mmHg" if datos.presion_sistolica is not None else "no disponible"
    colesterol = f"{datos.colesterol_total}mg/dL" if datos.colesterol_total is not None else "no disponible"

    user_data_table = f"""
Usuario | Edad: {datos.edad} | Sexo: {datos.genero} | IMC: {datos.imc} | Cintura: {datos.circunferencia_cintura}cm
Mediciones | Altura: {altura} | Peso: {peso} | Presión: {presion} | Colesterol: {colesterol}
Hábitos | Sueño: {datos.horas_sueno}h | Tabaco: {'Sí' if datos.tabaquismo else 'No'} | Actividad: {datos.actividad_fisica}
"""
    
    driver_descriptions = [d.description if hasattr(d, 'description') else str(d) for d in prediccion.drivers]
    
    user_prompt = f"""KB (JSON):
{contexto_rag}

Análisis:
• Riesgo: {prediccion.score:.2f} ({prediccion.categoria_riesgo})
• Drivers: {', '.join(driver_descriptions)}
{user_data_table}

Tarea: Explica riesgo "{prediccion.categoria_riesgo}" + 2-3 acciones concretas (2 semanas) usando KB. Cita cada recomendación. Max 150 palabras + disclaimer."""

    try:
        prompt_tokens_est = count_tokens(system_prompt) + count_tokens(user_prompt) + 10
        logger.info(f"📨 RAG prompt: ~{prompt_tokens_est} tokens")
        
        # Call Groq (using OpenAI-compatible API)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        plan_ia = completion.choices[0].message.content.strip()
        
        # Log usage
        if completion.usage:
            usage = completion.usage
            logger.info(f"💰 RAG API: Groq - {usage.prompt_tokens} in + {usage.completion_tokens} out = {usage.total_tokens} total")
        
        if "diagnóstico médico" not in plan_ia.lower():
             plan_ia += "\n\nRecuerda que esto no es un diagnóstico médico. Consulta a un profesional de la salud."

        # Verificar citas
        citas_reales_en_texto = []
        for cita in citas_kb:
            cita_patterns = [
                f"[Cita: {cita}]",
                f"[Cita:{cita}]",
                f"Cita: {cita}",
                f"Fuente: {cita}",
                cita
            ]
            if any(pattern in plan_ia for pattern in cita_patterns):
                citas_reales_en_texto.append(cita)
        
        if not citas_reales_en_texto and citas_kb:
            logger.warning("El LLM no incluyó citas en el formato esperado. Añadiendo al final.")
            citas_formateadas = [f"[Cita: {c}]" for c in citas_kb]
            plan_ia += f"\n\n**Fuentes consultadas:** {', '.join(citas_formateadas)}"
            citas_reales_en_texto = citas_kb
        elif citas_reales_en_texto:
            logger.info(f"Citas encontradas en el texto: {citas_reales_en_texto}")

        return plan_ia, citas_reales_en_texto

    except Exception as e:
        logger.error(f"Error en la API de Groq: {e}")
        raise Exception(f"Error al generar el plan personalizado: {e}")