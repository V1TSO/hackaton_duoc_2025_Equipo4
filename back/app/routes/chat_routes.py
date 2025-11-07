from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verify_supabase_token
from app.core.database import (
    get_or_create_session, 
    get_messages_by_session, 
    save_chat_message,
    save_assessment,
    link_assessment_to_session,
    get_supabase
)
from app.schemas.chat_schema import ChatMessageInput, ChatMessageOutput, ChatMessage
from app.agents.conversational_agent import process_chat_message
from app.agents.coach_agent import process_coach_message
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post(
    "/message", 
    response_model=ChatMessageOutput,
    summary="Endpoint principal de chat conversacional",
    tags=["Chat Agent"]
)
async def handle_chat_message(
    data: ChatMessageInput,
    usuario = Depends(verify_supabase_token)
):
    """
    Recibe un mensaje de chat, gestiona el contexto y decide si predecir.
    1. Obtiene o crea la sesión de chat.
    2. Guarda el mensaje del usuario.
    3. Carga el historial de chat.
    4. Llama al Agente Conversacional para procesar el historial.
    5. El Agente decide:
        a) Si faltan datos, devuelve la siguiente pregunta.
        b) Si los datos están completos, llama al ML (predict) y al RAG (coach).
    6. Guarda la respuesta del agente.
    7. Devuelve la respuesta y el estado al frontend.
    """
    user_id = usuario["id"]
    access_token = usuario.get("_access_token")
    
    # 1. Obtener o crear sesión
    session = get_or_create_session(user_id, data.session_id, access_token)
    if "error" in session:
        raise HTTPException(status_code=500, detail=session["error"])
    
    session_id_str = str(session['id'])

    # 2. Guardar mensaje de usuario
    save_chat_message(session_id_str, "user", data.content, access_token)

    # 3. Cargar historial de chat (para el LLM)
    history = get_messages_by_session(session_id_str, access_token)
    
    # 4. Procesar con el Agente Conversacional
    response_text, assessment_result, prediction_made = process_chat_message(history)

    # 5. Guardar respuesta del asistente
    assistant_message = save_chat_message(session_id_str, "assistant", response_text, access_token)

    # 6. Si se hizo una predicción, guardarla en 'assessments'
    assessment_id = None

    if prediction_made and assessment_result:
        assessment_result["user_id"] = user_id
        assessment_result.setdefault("model_used", "diabetes")
        saved_assessment = save_assessment(user_id, assessment_result, access_token)
        
        if "id" in saved_assessment:
            # Vincular el assessment a la sesión de chat
            link_assessment_to_session(session_id_str, str(saved_assessment["id"]), access_token)
            # (Opcional) Actualizar la tabla 'analisis_salud' también
            # ...lógica para guardar en 'analisis_salud' si aún se usa...
            assessment_id = saved_assessment["id"]

    # 7. Devolver respuesta al frontend
    # Volvemos a cargar el historial para que incluya los últimos mensajes
    final_history = get_messages_by_session(session_id_str, access_token)
    
    return ChatMessageOutput(
        session_id=session_id_str,
        response=ChatMessage(**assistant_message),
        history=[ChatMessage(**msg) for msg in final_history],
        prediction_made=prediction_made,
        model_used=assessment_result.get("model_used") if assessment_result else None,
        assessment_id=assessment_id
    )

@router.post(
    "/coach/message",
    summary="Chat endpoint for coaching with assessment context",
    tags=["Coach Chat"]
)
async def handle_coach_message(
    data: ChatMessageInput,
    usuario = Depends(verify_supabase_token)
):
    """
    Handles coach chat messages. Requires an assessment_id in the session_id field.
    The coach provides guidance based on the user's assessment and plan.
    """
    user_id = usuario["id"]
    access_token = usuario.get("_access_token")
    
    # The session_id should contain the assessment_id for coach chats
    assessment_id = data.session_id
    
    if not assessment_id:
        raise HTTPException(
            status_code=400,
            detail="assessment_id is required for coach chat"
        )
    
    # Load the assessment to get context
    supabase = get_supabase(access_token)
    try:
        assessment_response = supabase.table("assessments").select("*").eq("id", assessment_id).eq("user_id", user_id).single().execute()
        
        if not assessment_response.data:
            raise HTTPException(
                status_code=404,
                detail="Assessment not found"
            )
        
        assessment = assessment_response.data
        assessment_data = assessment
        
        # Extract plan text from assessment_data
        raw_assessment_data = assessment.get("assessment_data", {})
        plan_text = raw_assessment_data.get("plan_text", "No hay plan generado aún.")
        
    except Exception as e:
        logger.error(f"Error loading assessment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading assessment: {str(e)}"
        )
    
    # Get or create a coach session (separate from evaluation session)
    coach_session_key = f"coach_{assessment_id}"
    coach_session = get_or_create_session(user_id, coach_session_key, access_token)
    
    if "error" in coach_session:
        raise HTTPException(status_code=500, detail=coach_session["error"])
    
    coach_session_id = str(coach_session['id'])
    
    # Save user message
    save_chat_message(coach_session_id, "user", data.content, access_token)
    
    # Load conversation history
    history = get_messages_by_session(coach_session_id, access_token)
    
    # Process with coach agent
    coach_response = process_coach_message(assessment_data, plan_text, history)
    
    # Save assistant response
    assistant_message = save_chat_message(coach_session_id, "assistant", coach_response, access_token)
    
    # Return response
    final_history = get_messages_by_session(coach_session_id, access_token)
    
    return ChatMessageOutput(
        session_id=coach_session_id,
        response=ChatMessage(**assistant_message),
        history=[ChatMessage(**msg) for msg in final_history],
        prediction_made=False,
        model_used=None,
        assessment_id=assessment_id
    )