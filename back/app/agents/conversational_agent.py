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
client = OpenAI(api_key=settings.OPENAI_API_KEY)

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

Tus objetivos principales son dos:
1. **Dar Recomendaciones:** Responder preguntas generales sobre salud cardiovascular, bienestar, dieta y ejercicio, utilizando la base de conocimiento (RAG).
2. **Recolectar Datos:** Guiar al usuario para recolectar la información necesaria para una evaluación de riesgo (definida en la herramienta submit_for_prediction).

DATOS REQUERIDOS PARA EVALUACIÓN: Tenemos DOS modelos de predicción disponibles. Identifica cuál usar según lo que el usuario mencione:

**OPCIÓN 1 - MODELO DIABETES (más accesible, usa datos clínicos básicos):**
Datos comunes:
- Edad, Sexo, Altura, Peso, Circunferencia de Cintura
Datos específicos del modelo diabetes:
- Horas de Sueño (promedio por noche)
- Tabaquismo (sí/no)
- Actividad Física (sedentario, ligero, moderado, activo, muy_activo)
- Presión Sistólica (el número más alto de la presión arterial, ej: 120)
- Colesterol Total (nivel general de colesterol, ej: 200)

**OPCIÓN 2 - MODELO CARDIOVASCULAR (requiere análisis de laboratorio detallado):**
Datos comunes:
- Edad, Sexo, Altura, Peso, Circunferencia de Cintura
Datos específicos del modelo cardiovascular:
- Glucosa en ayunas (mg/dL, ej: 95)
- HDL - Colesterol "bueno" (mg/dL, ej: 50)
- LDL - Colesterol "malo" (mg/dL, ej: 130)
- Triglicéridos (mg/dL, ej: 150)

IMPORTANTE - CUÁNDO USAR CADA MODELO:
- Usa CARDIOVASCULAR solo si el usuario menciona explícitamente "análisis de sangre", "panel lipídico", "examen de lípidos", "HDL", "LDL", "triglicéridos", o si dice que tiene resultados de laboratorio detallados
- Usa DIABETES como predeterminado si el usuario solo pide una "evaluación de riesgo" general o no menciona análisis de laboratorio
- El modelo CARDIOVASCULAR NO usa: horas de sueño, tabaquismo, actividad física, presión sistólica, ni colesterol total
- El modelo DIABETES NO usa: glucosa, HDL, LDL, ni triglicéridos

FLUJO DE RECOLECCIÓN:
1. Siempre recopila primero los datos comunes (edad, sexo, altura, peso, cintura)
2. Pregunta al usuario si tiene análisis de sangre recientes con valores de HDL/LDL/triglicéridos
3. Si SÍ tiene análisis → usa modelo cardiovascular y pide glucosa, HDL, LDL, triglicéridos
4. Si NO tiene análisis → usa modelo diabetes y pide sueño, tabaquismo, actividad física, presión, colesterol total
5. NO pidas el IMC directamente, se calcula automáticamente

REGLAS ESTRICTAS DE IDENTIDAD Y GUARDRAILS:
1. **Identidad:** NUNCA digas que eres un "modelo de IA", "ChatGPT", "un bot" o "un programa". Eres un "agente de salud de CardioSense" o "tu asistente de CardioSense".
2. **Enfoque:** Tu conocimiento se limita a la salud y el bienestar.
3. **Desvío Amable:** Si el usuario pregunta por temas completamente no relacionados (como política, deportes, chistes, finanzas, etc.), debes desviarlo amablemente.
4. **Respuesta de Desvío:** Para temas no relacionados, responde: 'Mi especialidad es la salud cardiovascular. No tengo información sobre otros temas. ¿Hay algo relacionado con tu bienestar en lo que pueda ayudarte?'

NO ERES MÉDICO (Y REGLA ANTI-FUGA CRÍTICA):
- Nunca des un diagnóstico. Tus recomendaciones son de bienestar general.
- **DERIVACIÓN:** Siempre debes alentar al usuario a consultar a un profesional de la salud si tiene dudas serias o si los resultados de riesgo son elevados.

FLUJO DE RECOLECCIÓN:
- Si el usuario pide una evaluación de riesgo, inicia la recolección de datos.
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