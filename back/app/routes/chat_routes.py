from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verify_supabase_token
from app.core.database import (
    get_or_create_session, 
    get_messages_by_session, 
    save_chat_message,
    save_assessment,
    link_assessment_to_session
)
from app.schemas.chat_schema import ChatMessageInput, ChatMessageOutput, ChatMessage
from app.agents.conversational_agent import process_chat_message
import uuid

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