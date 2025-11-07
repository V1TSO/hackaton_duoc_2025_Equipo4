import logging
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

from app.core.config import settings
from app.schemas.analisis_schema import AnalisisEntrada, PrediccionResultado
from app.services.ml_service import obtener_prediccion
from app.agents.openai_agent import generar_plan_con_rag
from app.agents.sliding_window import get_optimized_history
from app.utils.token_counter import count_messages_tokens, estimate_cost

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# 1. Definición de la "Herramienta" (Tool Calling)
# El LLM intentará llenar este objeto Pydantic.

# Usamos AnalisisEntrada, pero lo re-definimos aquí para
# que Pydantic pueda generar un schema de tool-call limpio.
# Nota: Hacemos todos los campos REQUERIDOS.
class PredictionData(BaseModel):
    """
    Datos requeridos para ejecutar una predicción de salud.
    El agente DEBE recolectar esta información ANTES de llamar a la herramienta.
    """
    edad: int = Field(..., description="Edad del usuario en años.")
    genero: Literal['M', 'F'] = Field(..., description="Sexo biológico del usuario (M o F).")
    imc: float = Field(..., description="Índice de Masa Corporal (ej: 25.4).")
    circunferencia_cintura: float = Field(..., description="Circunferencia de cintura en centímetros (ej: 92.5).")
    altura_cm: float = Field(..., description="Altura del usuario en centímetros (ej: 170).")
    peso_kg: float = Field(..., description="Peso del usuario en kilogramos (ej: 75.5).")
    presion_sistolica: float = Field(..., description="Presión arterial sistólica (el número más alto, ej: 120).")
    colesterol_total: float = Field(..., description="Nivel de colesterol total (ej: 200).")
    tabaquismo: bool = Field(..., description="¿El usuario fuma? (true/false).")
    actividad_fisica: str = Field(..., description="Nivel de actividad física (ej: 'sedentario', 'moderado', 'activo').")
    horas_sueno: float = Field(..., description="Horas de sueño promedio por noche (ej: 7.5).")
    glucosa_mgdl: Optional[float] = Field(None, description="Nivel de glucosa en sangre (mg/dL), si está disponible.")
    hdl_mgdl: Optional[float] = Field(None, description="Colesterol HDL en mg/dL (opcional).")
    trigliceridos_mgdl: Optional[float] = Field(None, description="Triglicéridos en mg/dL (opcional).")
    ldl_mgdl: Optional[float] = Field(None, description="Colesterol LDL en mg/dL (opcional).")
    
    # Nuevo campo de tu requisito: decidir el modelo
    modelo_a_usar: Literal['diabetes', 'cardiovascular'] = Field(
        ..., 
        description="Basado en la conversación, decide qué modelo es más relevante. "
                    "Usa 'diabetes' si la preocupación principal es el azúcar en sangre. "
                    "Usa 'cardiovascular' si es presión arterial, colesterol o tabaquismo."
    )

# 2. El Prompt del Sistema

SYSTEM_PROMPT = """
Eres un Asistente de Salud IA empático y profesional.
Tu objetivo principal es recolectar la información necesaria para realizar una evaluación de riesgo.
Los datos que necesitas están definidos en la herramienta 'submit_for_prediction'.
NO pidas todos los datos a la vez. Hazlo de forma natural, una o dos preguntas por vez.
Sé amable y conversacional. Si el usuario da información no solicitada, tómala.
Una vez que tengas TODOS los datos requeridos, y SÓLO entonces, llama a la herramienta 'submit_for_prediction'.
Si te faltan datos, NO llames a la herramienta. En su lugar, haz la siguiente pregunta para obtener los datos faltantes.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "submit_for_prediction",
            "description": "Enviar datos de salud completos para realizar predicción de riesgo cardiometabólico",
            "parameters": PredictionData.model_json_schema()
        }
    }
]

# 3. El Orquestador Principal del Chat
def process_chat_message(history: List[dict]) -> tuple[str, dict | None, bool]:
    """
    Procesa un mensaje de usuario y decide el siguiente paso.
    
    Ahora con optimización de tokens:
    - Aplica sliding window al historial
    - Registra uso de tokens
    - Mantiene contexto relevante
    
    Returns:
        - response_content (str): La respuesta de texto del agente.
        - assessment_result (dict): El resultado de la predicción (si se hizo).
        - prediction_made (bool): Flag que indica si se completó la predicción.
    """
    logger.info(f"Procesando historial de {len(history)} mensajes.")
    
    # 1. Aplicar sliding window al historial
    optimized_history = get_optimized_history(
        history, 
        max_tokens=settings.TOKEN_BUDGET_HISTORY
    )
    
    # Log de optimización
    original_tokens = count_messages_tokens(history)
    optimized_tokens = count_messages_tokens(optimized_history)
    tokens_saved = original_tokens - optimized_tokens
    
    if tokens_saved > 0:
        logger.info(f"✂️  Sliding window aplicado: {original_tokens} → {optimized_tokens} tokens (ahorro: {tokens_saved})")
    else:
        logger.info(f"📊 Historial optimizado: {optimized_tokens} tokens (sin compresión necesaria)")
    
    # 2. Construir mensajes para OpenAI
    system_message = {"role": "system", "content": SYSTEM_PROMPT}
    messages_for_api = [system_message] + optimized_history
    
    # Contar tokens totales de entrada
    input_tokens = count_messages_tokens(messages_for_api)
    logger.info(f"📨 Tokens de entrada: {input_tokens} (sistema: {count_messages_tokens([system_message])}, historial: {optimized_tokens})")
    
    # 3. Llamar a OpenAI con el historial optimizado
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_for_api,
            tools=TOOLS,
            tool_choice="auto"
        )
        response_message = completion.choices[0].message
        
        # Registrar uso de tokens de la API
        usage = completion.usage
        if usage:
            output_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            cost = estimate_cost(usage.prompt_tokens, output_tokens)
            logger.info(f"💰 API Usage: {usage.prompt_tokens} in + {output_tokens} out = {total_tokens} total (~${cost:.4f})")
        
    except Exception as e:
        logger.error(f"Error en API de OpenAI: {e}")
        return "Lo siento, tuve un problema al procesar tu solicitud. Intenta de nuevo.", None, False

    # 2. Analizar la respuesta del LLM
    tool_calls = response_message.tool_calls
    
    # CASO A: El LLM llamó a la herramienta (¡Tenemos los datos!)
    if tool_calls:
        logger.info("OpenAI solicitó una llamada a herramienta. ¡Extrayendo datos!")
        try:
            # Asumimos que llama a la primera (y única) herramienta
            tool_call = tool_calls[0]
            tool_data = PredictionData.model_validate_json(tool_call.function.arguments)
            
            # ¡ÉXITO! Tenemos el JSON estructurado.
            # Ahora seguimos el flujo que TÚ describiste.
            
            # 2a. Decidir el modelo (según el LLM)
            modelo_elegido = tool_data.modelo_a_usar
            logger.info(f"Modelo elegido por el agente: {modelo_elegido}")
            
            # 2b. Llamar al servicio de predicción (nuestro /predict)
            # Pasamos los datos como AnalisisEntrada
            # (El schema es casi idéntico, Pydantic se encarga)
            tool_payload = tool_data.model_dump()
            modelo_elegido = tool_payload.pop("modelo_a_usar")

            ml_input = AnalisisEntrada(
                modelo=modelo_elegido,
                **tool_payload
            )
            
            # Aquí es donde realmente llamarías al modelo de 'diabetes' o 'cardiovascular'
            # Por ahora, ambos llaman al mismo servicio de Colab
            pred_result = obtener_prediccion(ml_input, model_type=modelo_elegido)
            
            if "error" in pred_result:
                return f"Tuve problemas al calcular tu predicción: {pred_result['error']}", None, False

            # 2c. Generar respuesta humanizada (nuestro /coach RAG)
            # Usamos el resultado de la predicción y los datos de entrada
            prediccion_schema = PrediccionResultado(
                score=pred_result['score'],
                drivers=pred_result['drivers'],
                categoria_riesgo=pred_result['categoria_riesgo'],
                model_used=pred_result.get('model_used', modelo_elegido)
            )

            plan_ia, citas_kb = generar_plan_con_rag(
                prediccion=prediccion_schema,
                datos=ml_input
            )

            # 2d. Preparar el resultado final
            final_response_text = (
                f"¡Gracias! He completado tu evaluación (usando el modelo de {modelo_elegido}).\n\n"
                f"**Resultado:** Tu riesgo es **{pred_result['categoria_riesgo']}**.\n\n"
                f"**Plan de Acción:**\n{plan_ia}"
            )
            
            assessment_data = {
                "assessment_data": tool_data.model_dump(),
                "risk_score": pred_result['score'],
                "risk_level": pred_result['categoria_riesgo'].lower(), # 'low', 'moderate', 'high'
                "drivers": pred_result['drivers'],
                "model_used": pred_result.get('model_used', modelo_elegido),
                "plan_text": plan_ia,
                "citations": citas_kb
            }
            
            return final_response_text, assessment_data, True

        except Exception as e:
            logger.error(f"Error al procesar la llamada a herramienta: {e}")
            return "Parece que tengo todos tus datos, pero tuve un problema al procesarlos. ¿Podrías confirmarlos?", None, False

    # CASO B: El LLM NO llamó a la herramienta (Sigue preguntando)
    else:
        logger.info("OpenAI respondió con texto (sigue recolectando datos).")
        response_text = response_message.content
        return response_text, None, False