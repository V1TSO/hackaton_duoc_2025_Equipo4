from pydantic import BaseModel, Field
from typing import Optional, List
import uuid

class ChatSession(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_id: uuid.UUID
    assessment_id: Optional[uuid.UUID] = None
    title: str = "Nueva conversación"

    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    session_id: uuid.UUID
    role: str # "user" o "assistant"
    content: str
    
    class Config:
        from_attributes = True

class ChatMessageInput(BaseModel):
    """Lo que el frontend envía al backend"""
    content: str
    session_id: Optional[uuid.UUID] = None # Opcional: si es nulo, creamos una nueva sesión

class ChatMessageOutput(BaseModel):
    """Lo que el backend devuelve al frontend"""
    session_id: uuid.UUID
    response: ChatMessage # La respuesta del asistente
    history: List[ChatMessage] # El historial actualizado
    prediction_made: bool = False # Flag para que el frontend sepa si se completó
    model_used: Optional[str] = None
    assessment_id: Optional[uuid.UUID] = None