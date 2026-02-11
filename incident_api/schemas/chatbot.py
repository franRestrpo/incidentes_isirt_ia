"""
Esquemas de Pydantic para la interacción con el chatbot de IA.
"""
from pydantic import BaseModel, Field
from typing import List
import datetime


class ChatbotRequest(BaseModel):
    """Esquema para una petición al chatbot."""
    prompt: str = Field(..., description="El prompt o pregunta del usuario.")
    conversation_id: str = Field(
        ...,
        description="Identificador único de la conversación para mantener el contexto."
    )
    is_start_of_conversation: bool = Field(
        False,
        description="Indica si este es el inicio de una nueva conversación."
    )


class ChatbotResponse(BaseModel):
    """Esquema para la respuesta del chatbot."""
    response: str = Field(..., description="La respuesta generada por el asistente de IA.")
    conversation_id: str = Field(
        ...,
        description="Identificador único de la conversación para mantener el contexto."
    )


# --- Esquemas para el Historial de Conversación ---

class ConversationHistoryBase(BaseModel):
    """Esquema base para una entrada en el historial de conversación."""
    role: str = Field(..., description="Rol del autor del mensaje (user o assistant).")
    message_content: str = Field(..., description="Contenido del mensaje.")


class ConversationHistoryCreate(ConversationHistoryBase):
    """Esquema para crear una nueva entrada en el historial."""
    conversation_id: str


class ConversationHistoryInDB(ConversationHistoryBase):
    """Esquema para leer una entrada del historial desde la BD."""
    id: int
    user_id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True
