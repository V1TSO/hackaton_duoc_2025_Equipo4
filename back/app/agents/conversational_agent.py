# back/app/agents/conversational_agent.py
import logging
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
import json # Importa json

from app.core.config import settings
# Asegúrate de que las rutas de importación sean correctas
from app.schemas.analisis_schema import AnalisisEntrada, PrediccionResultado
from app.services.ml_service import obtener_prediccion
from app.agents.openai_agent import generar_plan_con_rag

logger = logging.getLogger(__name__)

# Use Groq client if available, otherwise try OpenAI
if settings.GROQ_API_KEY:
    client = OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )
    DEFAULT_MODEL = "llama-3.1-8b-instant"
elif settings.OPENAI_API_KEY:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    DEFAULT_MODEL = "gpt-4o-mini"
else:
    client = None
    DEFAULT_MODEL = None
    logger.warning("No LLM API key configured. Chat features will be disabled.")

# 1. Definición de la "Herramienta" (Tool Calling)
class PredictionData(BaseModel):
    """
    Datos requeridos para ejecutar una predicción de salud.
    El agente DEBE recolectar esta información ANTES de llamar a la herramienta.
    """
    # Campos comunes a ambos modelos (siempre requeridos)
    edad: int = Field(..., description="Edad del usuario en años.")
    genero: Literal['M', 'F'] = Field(..., description="Sexo biológico del usuario (M o F).")
    altura_cm: float = Field(..., description="Altura del usuario en centímetros (ej: 170).")
    peso_kg: float = Field(..., description="Peso del usuario en kilogramos (ej: 75).")
    circunferencia_cintura: float = Field(..., description="Circunferencia de cintura en centímetros (ej: 92.5).")
    imc: Optional[float] = Field(None, description="Índice de Masa Corporal (calculado automáticamente).")
    
    # Campos SOLO para modelo diabetes
    presion_sistolica: Optional[float] = Field(None, description="Presión arterial sistólica (ej: 120). REQUERIDO SOLO para modelo diabetes.")
    colesterol_total: Optional[float] = Field(None, description="Colesterol total (ej: 200). REQUERIDO SOLO para modelo diabetes.")
    horas_sueno: Optional[float] = Field(None, description="Horas de sueño por noche (ej: 7.5). REQUERIDO SOLO para modelo diabetes.")
    tabaquismo: Optional[bool] = Field(None, description="¿Fuma? REQUERIDO SOLO para modelo diabetes.")
    actividad_fisica: Optional[str] = Field(None, description="Nivel de actividad ('sedentario','moderado','activo'). REQUERIDO SOLO para modelo diabetes.")
    
    # Campos SOLO para modelo cardiovascular
    glucosa_mgdl: Optional[float] = Field(None, description="Glucosa en ayunas mg/dL (ej: 95). REQUERIDO SOLO para modelo cardiovascular.")
    hdl_mgdl: Optional[float] = Field(None, description="HDL colesterol bueno mg/dL (ej: 50). REQUERIDO SOLO para modelo cardiovascular.")
    ldl_mgdl: Optional[float] = Field(None, description="LDL colesterol malo mg/dL (ej: 130). REQUERIDO SOLO para modelo cardiovascular.")
    trigliceridos_mgdl: Optional[float] = Field(None, description="Triglicéridos mg/dL (ej: 150). REQUERIDO SOLO para modelo cardiovascular.")
    
    modelo_a_usar: Literal['diabetes', 'cardiovascular'] = Field(
        ..., 
        description="Basado en la conversación y los datos disponibles, decide qué modelo es más relevante. "
                    "IMPORTANTE: Usa 'cardiovascular' SOLO si tienes valores de HDL, LDL y triglicéridos. "
                    "Si solo tienes colesterol total y presión sistólica, usa 'diabetes'. "
                    "El modelo 'diabetes' usa presión sistólica y colesterol total directamente. "
                    "El modelo 'cardiovascular' requiere HDL, LDL, triglicéridos y glucosa."
    )

# 2. El Prompt del Sistema (¡MODIFICADO CON GUARDRAILS!)
SYSTEM_PROMPT = """
Eres un agente de salud conversacional de CardioSense. Tu identidad es ser un asistente de salud empático y profesional de CardioSense.

**IMPORTANTE - CUANDO LLAMAR A LA HERRAMIENTA submit_for_prediction:**
Solo debes llamar a submit_for_prediction cuando tengas TODOS estos datos:

PARA MODELO DIABETES (si el usuario NO tiene análisis de sangre):
- edad (número)
- genero (M o F)
- altura_cm (número)
- peso_kg (número)
- circunferencia_cintura (número)
- horas_sueno (número, ej: 7)
- tabaquismo (true/false)
- actividad_fisica (sedentario, ligero, moderado, activo, muy_activo)
- presion_sistolica (número, ej: 120)
- colesterol_total (número, ej: 200)
- modelo_a_usar: "diabetes"

PARA MODELO CARDIOVASCULAR (si el usuario SÍ tiene análisis de sangre):
- edad (número)
- genero (M o F)
- altura_cm (número)
- peso_kg (número)
- circunferencia_cintura (número)
- glucosa_mgdl (número)
- hdl_mgdl (número)
- ldl_mgdl (número)
- trigliceridos_mgdl (número)
- modelo_a_usar: "cardiovascular"

**MUY IMPORTANTE:**
- SIEMPRE incluye el campo "modelo_a_usar" con valor "diabetes" o "cardiovascular"
- NO inventes valores. Si no los tienes, pregunta al usuario.
- Verifica que todos los campos estén presentes antes de llamar a la herramienta.

REGLAS:
1. **Identidad:** NUNCA digas que eres un "modelo de IA", "ChatGPT", "un bot" o "un programa". Eres un "agente de salud de CardioSense".
2. **NO ERES MÉDICO:** Nunca des un diagnóstico. Recomienda consultar a un profesional.
3. **Desvío:** Si preguntan sobre temas no relacionados a salud, responde: 'Mi especialidad es la salud cardiovascular. ¿Hay algo relacionado con tu bienestar en lo que pueda ayudarte?'

FLUJO:
1. El usuario pide una evaluación → pregunta datos básicos (edad, sexo, altura, peso, cintura)
2. Pregunta si tiene análisis de sangre recientes (HDL, LDL, triglicéridos)
3. Si SÍ tiene → pide modelo cardiovascular (glucosa, HDL, LDL, triglicéridos)
4. Si NO tiene → pide modelo diabetes (horas_sueno, tabaquismo, actividad_fisica, presion_sistolica, colesterol_total)
5. Cuando tengas TODOS los datos, llama a submit_for_prediction
- Explica que necesitas información sobre su perfil y estilo de vida para generar el perfil de riesgo.
- Pide los datos de forma natural, una o dos preguntas por vez.
- **CONFIRMACIÓN:** Una vez que tengas TODOS los datos, resúmelos al usuario (ej. "¡Perfecto! Déjame confirmar...")
- Tras la confirmación del usuario, y SÓLO entonces, llama a la herramienta submit_for_prediction.
- Si te faltan datos, NO llames a la herramienta. En su lugar, haz la siguiente pregunta para obtener los datos faltantes.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "submit_for_prediction",
            "description": "Envía los datos recolectados del usuario para calcular la predicción de riesgo de salud. Llama a esta función SOLO cuando tengas TODOS los datos requeridos.",
            "parameters": PredictionData.model_json_schema()
        }
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
            model=DEFAULT_MODEL, 
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
            
            # Calcular IMC si no se proporcionó pero tenemos altura y peso
            if ml_input_data.get('imc') is None:
                altura = ml_input_data.get('altura_cm')
                peso = ml_input_data.get('peso_kg')
                if altura and peso and altura > 0:
                    ml_input_data['imc'] = peso / ((altura / 100) ** 2)
                    logger.info(f"IMC calculado automáticamente: {ml_input_data['imc']:.2f} (peso: {peso}kg, altura: {altura}cm)")
            
            # Validar que el modelo seleccionado sea apropiado para los datos disponibles
            # El modelo cardiovascular requiere HDL, LDL, triglicéridos (TODOS)
            # El modelo diabetes usa presión sistólica y colesterol total
            tiene_hdl_ldl_trig = (ml_input_data.get('hdl_mgdl') is not None and 
                                  ml_input_data.get('ldl_mgdl') is not None and 
                                  ml_input_data.get('trigliceridos_mgdl') is not None)
            tiene_presion_colesterol = (ml_input_data.get('presion_sistolica') is not None and 
                                       ml_input_data.get('colesterol_total') is not None)
            
            # Si el agente eligió cardiovascular pero no tenemos HDL/LDL/trig completos, usar diabetes
            if modelo_elegido == "cardiovascular" and not tiene_hdl_ldl_trig:
                if tiene_presion_colesterol:
                    logger.warning(f"⚠️ El agente eligió 'cardiovascular' pero faltan datos completos de lípidos (HDL/LDL/triglicéridos). "
                                 f"Cambiando a 'diabetes' que usa presión y colesterol total.")
                    modelo_elegido = "diabetes"
                    ml_input_data['modelo'] = "diabetes"
                else:
                    logger.error(f"❌ Modelo cardiovascular requiere HDL, LDL y triglicéridos, pero no están disponibles.")
                    return "Lo siento, para usar el modelo cardiovascular necesito los valores de HDL, LDL y triglicéridos. ¿Podrías proporcionarlos?", None, False
            
            ml_input = AnalisisEntrada(**ml_input_data) 
            
            # Llamamos al servicio de ML con el modelo seleccionado (posiblemente corregido)
            pred_result = obtener_prediccion(ml_input, model_type=modelo_elegido)
            logger.info(f"Predicción obtenida con modelo '{modelo_elegido}': score={pred_result.get('score')}, risk_level={pred_result.get('categoria_riesgo')}")
            
            if "error" in pred_result:
                return f"Tuve problemas al calcular tu predicción: {pred_result['error']}", None, False

            # Convert dict to PrediccionResultado Pydantic object
            prediccion_obj = PrediccionResultado(**pred_result)
            
            # Generar respuesta humanizada (nuestro /coach RAG)
            logger.info("Generando plan con RAG...")
            plan_ia, citas_kb = generar_plan_con_rag(
                prediccion=prediccion_obj,
                datos=ml_input
            )
            logger.info(f"Plan generado exitosamente. Longitud: {len(plan_ia)} caracteres, Citas: {len(citas_kb)}")

            # Preparar el resultado final con guardrails
            REFERRAL_THRESHOLD = 0.70
            derivation_message = ""
            if prediccion_obj.score >= REFERRAL_THRESHOLD:
                derivation_message = (
                    f"\n\n⚠️ **IMPORTANTE - Derivación Recomendada:**\n"
                    f"Tu puntaje de riesgo ({prediccion_obj.score:.1%}) es elevado. "
                    f"Te recomendamos encarecidamente consultar con un profesional de la salud "
                    f"para una evaluación médica completa. Este sistema no reemplaza el diagnóstico médico profesional.\n"
                )
            elif prediccion_obj.categoria_riesgo.lower() == "alto":
                derivation_message = (
                    f"\n\n⚠️ **Recomendación:**\n"
                    f"Considera consultar con un profesional de la salud para una evaluación personalizada. "
                    f"Este sistema es una herramienta educativa y no reemplaza el consejo médico profesional.\n"
                )
            
            # Preparar el resultado final
            final_response_text = (
                f"¡Gracias! He completado tu evaluación (usando el modelo de {modelo_elegido}).\n\n"
                f"**Resultado:** Tu riesgo es **{prediccion_obj.categoria_riesgo}** "
                f"(puntaje: {prediccion_obj.score:.1%}).\n\n"
                f"**Plan de Acción:**\n{plan_ia}"
                f"{derivation_message}"
            )
            
            # Preparamos los datos completos para el frontend
            user_data = tool_data.model_dump()
            user_data["model_used"] = modelo_elegido
            user_data["plan_text"] = plan_ia
            user_data["citations"] = citas_kb
            logger.info(f"Datos del usuario preparados con plan_text y {len(citas_kb)} citas")
            
            # Preparamos el dict para la tabla 'assessments'
            assessment_data = {
                "assessment_data": user_data,
                "risk_score": prediccion_obj.score,
                "risk_level": prediccion_obj.categoria_riesgo.lower(), # 'low', 'moderate', 'high'
                "drivers": prediccion_obj.drivers
            }
            
            logger.info(f"Assessment data preparado: risk_score={prediccion_obj.score}, risk_level={prediccion_obj.categoria_riesgo.lower()}, tiene plan_text={('plan_text' in user_data)}")
            
            return final_response_text, assessment_data, True

        except Exception as e:
            logger.error(f"Error al procesar la llamada a herramienta: {e}")
            return "Parece que tengo todos tus datos, pero tuve un problema al procesarlos. ¿Podrías confirmarlos?", None, False

    # CASO B: El LLM NO llamó a la herramienta (Sigue preguntando o desvía)
    else:
        logger.info("OpenAI respondió con texto (recolectando datos o desviando).")
        response_text = response_message.content
        return response_text, None, False