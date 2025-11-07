from openai import OpenAI
from app.core.config import settings
from app.agents.rag_service import buscar_en_kb
from app.schemas.analisis_schema import AnalisisEntrada, PrediccionResultado
from app.utils.token_counter import count_tokens, estimate_cost
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generar_plan_con_rag(
    prediccion: PrediccionResultado, 
    datos: AnalisisEntrada
) -> tuple[str, list[str]]:
    
    logger.info(f"Generando plan RAG (JSON-Input) para riesgo: {prediccion.categoria_riesgo}")
    try:
        contexto_rag, citas_kb = buscar_en_kb(prediccion.drivers)
    except Exception as e:
        logger.error(f"Fallo en 'buscar_en_kb': {e}")
        # Fallback: le pasamos un JSON array vacío
        contexto_rag, citas_kb = "[]", [] 

    # Optimized: More concise system prompt (~30% reduction)
    system_prompt = """Coach de salud preventivo. NO das diagnósticos.
Genera plan de acción breve (3-4 recomendaciones) basado SOLO en el KB JSON.
Cita fuentes: [Cita: nombre]. Máximo 150 palabras. Incluye disclaimer médico."""

    # Optimized: Tabular format for user data (more token-efficient)
    altura = f"{datos.altura_cm}cm" if datos.altura_cm is not None else "N/D"
    peso = f"{datos.peso_kg}kg" if datos.peso_kg is not None else "N/D"
    presion = f"{datos.presion_sistolica}mmHg" if datos.presion_sistolica is not None else "N/D"
    colesterol = f"{datos.colesterol_total}mg/dL" if datos.colesterol_total is not None else "N/D"

    user_data_table = f"""
Usuario | Edad: {datos.edad} | Sexo: {datos.genero} | IMC: {datos.imc} | Cintura: {datos.circunferencia_cintura}cm
Mediciones | Altura: {altura} | Peso: {peso} | Presión: {presion} | Colesterol: {colesterol}
Hábitos | Sueño: {datos.horas_sueno}h | Tabaco: {'Sí' if datos.tabaquismo else 'No'} | Actividad: {datos.actividad_fisica}
"""
    
    # Optimized: More concise user prompt
    user_prompt = f"""KB (JSON):
{contexto_rag}

Análisis:
• Riesgo: {prediccion.score:.2f} ({prediccion.categoria_riesgo})
• Drivers: {', '.join(prediccion.drivers)}
{user_data_table}

Tarea: Explica riesgo "{prediccion.categoria_riesgo}" + 2-3 acciones concretas (2 semanas) usando KB. Cita cada recomendación. Max 150 palabras + disclaimer.
"""

    try:
        # Log token usage before API call
        messages_for_api = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        prompt_tokens_est = count_tokens(system_prompt) + count_tokens(user_prompt) + 10  # +10 for formatting
        logger.info(f"📨 RAG prompt: ~{prompt_tokens_est} tokens (sistema: {count_tokens(system_prompt)}, KB+datos: {count_tokens(user_prompt)})")
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_for_api,
            temperature=0.5,
            max_tokens=500,  # Explicit limit for 150-word response (~200 tokens) + safety margin
        )
        plan_ia = completion.choices[0].message.content.strip()
        
        # Log actual API usage
        if completion.usage:
            usage = completion.usage
            cost = estimate_cost(usage.prompt_tokens, usage.completion_tokens)
            logger.info(f"💰 RAG API: {usage.prompt_tokens} in + {usage.completion_tokens} out = {usage.total_tokens} total (~${cost:.4f})")

        
        if "diagnóstico médico" not in plan_ia.lower():
             plan_ia += "\n\nRecuerda que esto no es un diagnóstico médico. Consulta a un profesional de la salud."

        citas_reales_en_texto = [c for c in citas_kb if c in plan_ia]
        if not citas_reales_en_texto and citas_kb:
            logger.warning("El LLM no incluyó citas en el texto. Añadiendo al final.")
            plan_ia += f"\n\nFuentes: {', '.join(citas_kb)}"
            citas_reales_en_texto = citas_kb

        return plan_ia, citas_reales_en_texto

    except Exception as e:
        logger.error(f"Error en la API de OpenAI: {e}")
        plan_ia = (
            "El servicio de generación de planes personalizados no está disponible en este momento. "
            "Por favor, inténtalo nuevamente más tarde."
        )
        return plan_ia, []