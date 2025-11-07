# back/app/agents/coach_agent.py
import logging
from openai import OpenAI
from typing import List, Dict
import json

from app.core.config import settings
from app.agents.openai_agent import retrieve_context_from_kb

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def create_coach_system_prompt(assessment_data: Dict, plan_text: str) -> str:
    """
    Creates a system prompt for the coach agent that includes the user's assessment and plan.
    """
    
    # Extract key information from assessment
    risk_level = assessment_data.get("risk_level", "unknown")
    model_used = assessment_data.get("model_used", "unknown")
    
    # Get profile info
    profile = assessment_data.get("assessment_data", {})
    edad = profile.get("edad", "unknown")
    genero = profile.get("genero", "unknown")
    imc = profile.get("imc", "unknown")
    
    system_prompt = f"""
Eres un coach de salud profesional de CardioSense, experto en salud cardiovascular y metabólica.

CONTEXTO DEL USUARIO:
- Nivel de riesgo: {risk_level}
- Modelo utilizado: {model_used}
- Edad: {edad}
- Género: {genero}
- IMC: {imc}

PLAN PERSONALIZADO ACTUAL:
{plan_text}

TU ROL COMO COACH:
1. Eres un coach de apoyo que ayuda al usuario a seguir su plan personalizado
2. Respondes preguntas sobre el plan, las recomendaciones y cómo implementarlas
3. Das consejos prácticos y motivación
4. Explicas conceptos de salud de manera simple y accesible
5. Siempre haces referencia al plan cuando sea relevante

REGLAS IMPORTANTES:
- Nunca diagnostiques enfermedades
- Siempre recomienda consultar con un profesional de la salud para dudas médicas serias
- Mantente dentro del contexto de salud y bienestar
- Sé empático, motivador y positivo
- Da respuestas concisas (máximo 2-3 párrafos)
- Usa un lenguaje simple, evita términos médicos complejos
- Cuando sea posible, da ejemplos prácticos y accionables

CÓMO RESPONDER:
- Si te preguntan sobre el plan, cita las secciones relevantes
- Si te preguntan "cómo empezar", sugiere comenzar con las recomendaciones más simples
- Si te preguntan sobre progreso, recuerda que pueden actualizar su evaluación después de 2-4 semanas
- Si la pregunta no está relacionada con salud, redirige amablemente al tema de salud
"""
    
    return system_prompt

def process_coach_message(assessment_data: Dict, plan_text: str, history: List[dict]) -> str:
    """
    Processes a coach chat message with context about the user's assessment and plan.
    
    Args:
        assessment_data: The user's assessment data including risk level, profile, etc.
        plan_text: The personalized plan text generated for the user
        history: List of previous messages in the conversation
        
    Returns:
        The coach's response as a string
    """
    logger.info(f"Processing coach message with {len(history)} messages in history")
    
    # Create the system prompt with context
    system_prompt = create_coach_system_prompt(assessment_data, plan_text)
    
    # Get the user's latest message
    if not history or len(history) == 0:
        return "Hola, soy tu coach de CardioSense. ¿En qué puedo ayudarte hoy con tu plan de salud?"
    
    latest_message = history[-1]["content"]
    
    # Try to retrieve relevant context from knowledge base
    try:
        kb_context = retrieve_context_from_kb(latest_message, top_k=2)
        if kb_context:
            # Add RAG context to system prompt
            system_prompt += f"\n\nCONOCIMIENTO ADICIONAL DE LA BASE DE DATOS:\n{kb_context}"
    except Exception as e:
        logger.warning(f"Could not retrieve KB context: {e}")
    
    # Call OpenAI with the coach system prompt
    try:
        messages = [{"role": "system", "content": system_prompt}] + history
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        response = completion.choices[0].message.content
        logger.info("Coach response generated successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error calling OpenAI for coach: {e}")
        return "Lo siento, tuve un problema al procesar tu mensaje. Por favor intenta de nuevo."

