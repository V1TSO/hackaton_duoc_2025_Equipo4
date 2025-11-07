# back/app/agents/conversational_agent.py
import logging
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Literal
import json # Importa json

from app.core.config import settings
# Asegúrate de que las rutas de importación sean correctas
from app.schemas.analisis_schema import AnalisisEntrada
from app.services.ml_service import obtener_prediccion
from app.agents.openai_agent import generar_plan_con_rag

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# 1. Definición de la "Herramienta" (Tool Calling)
class PredictionData(BaseModel):
    """
    Datos requeridos para ejecutar una predicción de salud.
    El agente DEBE recolectar esta información ANTES de llamar a la herramienta.
    """
    edad: int = Field(..., description="Edad del usuario en años.")
    genero: Literal['M', 'F'] = Field(..., description="Sexo biológico del usuario (M o F).")
    imc: float = Field(..., description="Índice de Masa Corporal (ej: 25.4).")
    circunferencia_cintura: float = Field(..., description="Circunferencia de cintura en centímetros (ej: 92.5).")
    presion_sistolica: float = Field(..., description="Presión arterial sistólica (el número más alto, ej: 120).")
    colesterol_total: float = Field(..., description="Nivel de colesterol total (ej: 200).")
    tabaquismo: bool = Field(..., description="¿El usuario fuma? (true/false).")
    actividad_fisica: str = Field(..., description="Nivel de actividad física (ej: 'sedentario', 'moderado', 'activo').")
    horas_sueno: float = Field(..., description="Horas de sueño promedio por noche (ej: 7.5).")
    
    modelo_a_usar: Literal['diabetes', 'cardiovascular'] = Field(
        ..., 
        description="Basado en la conversación, decide qué modelo es más relevante. "
                    "Usa 'diabetes' si la preocupación principal es el azúcar en sangre. "
                    "Usa 'cardiovascular' si es presión arterial, colesterol o tabaquismo."
    )

# 2. El Prompt del Sistema (¡MODIFICADO CON GUARDRAILS!)
SYSTEM_PROMPT = SYSTEM_PROMPT = """
Eres un agente de salud conversacional de CardioSense.
Tu identidad es ser un asistente de salud empático y profesional de CardioSense.

Tus objetivos principales son dos:
1.  **Dar Recomendaciones:** Responder preguntas generales sobre salud cardiovascular, bienestar, dieta y ejercicio.
2.  **Recolectar Datos:** Guiar al usuario para recolectar la información necesaria para una evaluación de riesgo (definida en la herramienta 'submit_for_prediction').

REGLAS ESTRICTAS DE IDENTIDAD Y GUARDRAILS:
1.  **Identidad:** NUNCA digas que eres un "modelo de IA", "ChatGPT", "un bot" o "un programa". Eres un "agente de salud de CardioSense" o "tu asistente de CardioSense".
2.  **Enfoque:** Tu conocimiento se limita a la salud y el bienestar.
3.  **Desvío Amable:** Si el usuario pregunta por temas *completamente no relacionados* (como política, deportes, chistes, finanzas, etc.), debes desviarlo amablemente.
4.  **Respuesta de Desvío:** Para temas no relacionados, responde: 'Mi especialidad es la salud cardiovascular. No tengo información sobre otros temas. ¿Hay algo relacionado con tu bienestar en lo que pueda ayudarte?'
5.  **NO ERES MÉDICO:** Nunca des un diagnóstico. Tus recomendaciones son de bienestar general. Siempre debes alentar al usuario a consultar a un profesional de la salud si tiene dudas serias.

FLUJO DE RECOLECCIÓN:
-   Si el usuario pide una evaluación de riesgo, inicia la recolección de datos.
-   Los datos que necesitas están definidos en la herramienta 'submit_for_prediction'.
-   Pide los datos de forma natural, una o dos preguntas por vez.
-   Una vez que tengas TODOS los datos requeridos, y SÓLO entonces, llama a la herramienta 'submit_for_prediction'.
-   Si te faltan datos, NO llames a la herramienta. En su lugar, haz la siguiente pregunta para obtener los datos faltantes.
"""

TOOLS = [
    {
        "type": "function",
        # Usamos .model_json_schema() para la nueva versión de Pydantic
        "function": PredictionData.model_json_schema() 
    }
]

# 3. El Orquestador Principal del Chat
def process_chat_message(history: List[dict]) -> tuple[str, dict | None, bool]:
    """
    Procesa un mensaje de usuario y decide el siguiente paso.
    
    Returns:
        - response_content (str): La respuesta de texto del agente.
        - assessment_result (dict): El resultado de la predicción (si se hizo).
        - prediction_made (bool): Flag que indica si se completó la predicción.
    """
    logger.info(f"Procesando historial de {len(history)} mensajes.")
    
    # 1. Llamar a OpenAI con el historial y las herramientas
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            tools=TOOLS,
            tool_choice="auto"
        )
        response_message = completion.choices[0].message
    except Exception as e:
        logger.error(f"Error en API de OpenAI: {e}")
        return "Lo siento, tuve un problema al procesar tu solicitud. Intenta de nuevo.", None, False

    # 2. Analizar la respuesta del LLM
    tool_calls = response_message.tool_calls
    
    # CASO A: El LLM llamó a la herramienta (¡Tenemos los datos!)
    if tool_calls:
        logger.info("OpenAI solicitó una llamada a herramienta. ¡Extrayendo datos!")
        try:
            tool_call = tool_calls[0]
            # Validamos el JSON que nos pasó el LLM
            tool_data = PredictionData.model_validate_json(tool_call.function.arguments)
            
            modelo_elegido = tool_data.modelo_a_usar
            logger.info(f"Modelo elegido por el agente: {modelo_elegido}")
            
            # Convertimos los datos de Pydantic a un schema AnalisisEntrada
            # El schema de Pydantic se encarga de la conversión
            ml_input_data = tool_data.model_dump()
            # Añadimos 'fecha' si no está, aunque el modelo ML no la use
            ml_input_data.setdefault('fecha', '2025-01-01') 
            
            ml_input = AnalisisEntrada(**ml_input_data) 
            
            # Llamamos al servicio de ML
            # NOTA: Aquí deberías tener lógica para elegir el endpoint
            # correcto basado en 'modelo_elegido'.
            # Por ahora, usamos el 'obtener_prediccion' genérico.
            pred_result = obtener_prediccion(ml_input)
            
            if "error" in pred_result:
                return f"Tuve problemas al calcular tu predicción: {pred_result['error']}", None, False

            # Generar respuesta humanizada (nuestro /coach RAG)
            plan_ia, citas_kb = generar_plan_con_rag(
                prediccion=pred_result,
                datos=ml_input
            )

            # Preparar el resultado final
            final_response_text = (
                f"¡Gracias! He completado tu evaluación (usando el modelo de {modelo_elegido}).\n\n"
                f"**Resultado:** Tu riesgo es **{pred_result['categoria_riesgo']}**.\n\n"
                f"**Plan de Acción:**\n{plan_ia}"
            )
            
            # Preparamos el dict para la tabla 'assessments'
            assessment_data = {
                "assessment_data": user_input_data,
                "risk_score": pred_result['score'],
                "risk_level": pred_result['categoria_riesgo'].lower(), # 'low', 'moderate', 'high'
                "drivers": json.dumps(pred_result['drivers']) # Aseguramos que 'drivers' sea JSON
            }
            
            return final_response_text, assessment_data, True

        except Exception as e:
            logger.error(f"Error al procesar la llamada a herramienta: {e}")
            return "Parece que tengo todos tus datos, pero tuve un problema al procesarlos. ¿Podrías confirmarlos?", None, False

    # CASO B: El LLM NO llamó a la herramienta (Sigue preguntando o desvía)
    else:
        logger.info("OpenAI respondió con texto (recolectando datos o desviando).")
        response_text = response_message.content
        return response_text, None, False