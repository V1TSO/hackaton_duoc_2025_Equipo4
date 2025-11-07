from openai import OpenAI
from app.core.config import settings
from app.agents.rag_service import buscar_en_kb
from app.schemas.analisis_schema import AnalisisEntrada, PrediccionResultado
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

    system_prompt = """
    Eres un coach de bienestar preventivo, empático y responsable.
    NO eres médico. NO entregas diagnósticos ni tratamientos.
    Tu objetivo es generar un plan de acción basado *exclusivamente* en el contexto de la base de conocimiento (KB) proporcionada, la cual está en formato JSON.
    Debes citar tus fuentes usando el campo "cita" del JSON, en el formato [Cita: nombre_cita] al final de cada recomendación.
    NO puedes alucinar información ni inventar fuentes.
    Tu respuesta debe ser un plan de acción breve (3-4 recomendaciones), motivador y en español.
    """

    user_data_summary = (
        f"Datos del usuario: Edad: {datos.edad}, Género: {datos.genero}, "
        f"IMC: {datos.imc}, Cintura: {datos.circunferencia_cintura} cm, "
        f"Sueño: {datos.horas_sueno}h, Tabaco: {'Sí' if datos.tabaquismo else 'No'}, "
        f"Actividad: {datos.actividad_fisica}."
    )
    
    # El prompt de usuario AHORA inyecta un JSON
    user_prompt = f"""
    Contexto de la Base de Conocimiento (KB) en formato JSON:
    ---
    {contexto_rag}
    ---
    
    Datos del Análisis:
    - Riesgo Predicho: {prediccion.score:.2f} (Categoría: {prediccion.categoria_riesgo})
    - Factores Clave (Drivers): {', '.join(prediccion.drivers)}
    - {user_data_summary}

    Tarea:
    Basándote *exclusivamente* en el "Contexto de la Base de Conocimiento (KB) en formato JSON":
    1. Explica brevemente qué significa un riesgo "{prediccion.categoria_riesgo}".
    2. Ofrece 2-3 recomendaciones *concretas* para las próximas 2 semanas, usando el campo "texto" de los objetos JSON relevantes a los "Factores Clave (Drivers)".
    3. Cita *obligatoriamente* cada recomendación con el campo "cita" del objeto JSON correspondiente (ej: [Cita: guia_metabolica_v1]).
    4. Incluye un *disclaimer* final claro: "Recuerda que esto no es un diagnóstico médico. Consulta a un profesional de la salud."
    
    Responde en no más de 150 palabras.
    """

    try:
        logger.info("Llamando a la API de OpenAI con contexto RAG (JSON)...")
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
        )
        plan_ia = completion.choices[0].message.content.strip()
        
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
            f"Tu resultado sugiere un riesgo {prediccion.categoria_riesgo}. "
            f"Te puede ayudar mantener una alimentación equilibrada y moverte al menos 30 minutos al día. "
            f"Esto no es un diagnóstico médico. Consulta a un profesional de la salud."
        )
        return plan_ia, ["guia_general_v1"]