"""
Servicio para la gestión del historial de conversaciones del chatbot.
"""

import logging
from sqlalchemy.orm import Session
from typing import List

from incident_api import crud, schemas, models

logger = logging.getLogger(__name__)


class ConversationHistoryService:
    """
    Servicio para manejar la persistencia del historial de conversaciones.
    """

    def save_message(self, db: Session, conversation_id: str, user_id: int, role: str, content: str):
        """
        Guarda un único mensaje en la base de datos dentro del historial de una conversación.
        """
        message_in = schemas.ConversationHistoryCreate(
            conversation_id=conversation_id, role=role, message_content=content
        )
        crud.conversation_history.create(db, obj_in=message_in, user_id=user_id)

    def get_history_messages(self, db: Session, conversation_id: str) -> List[models.ConversationHistory]:
        """
        Obtiene el historial de mensajes de una conversación desde la base de datos.
        """
        return crud.conversation_history.get_by_conversation_id(db, conversation_id=conversation_id)


conversation_history_service = ConversationHistoryService()