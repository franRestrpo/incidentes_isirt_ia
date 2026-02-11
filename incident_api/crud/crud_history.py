"""
Operaciones CRUD para los modelos de historiales.
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from incident_api.crud.base import CRUDBase
from incident_api.models.history import IncidentHistory, ConversationHistory
from incident_api.schemas.incident_history import IncidentHistoryCreate
from incident_api.schemas.chatbot import ConversationHistoryCreate

# --- CRUD para IncidentHistory ---


class CRUDIncidentHistory(
    CRUDBase[IncidentHistory, IncidentHistoryCreate, IncidentHistoryCreate]
):
    """
    Clase CRUD para IncidentHistory, conservando métodos existentes.
    """

    def create(
        self,
        db: Session,
        *,
        obj_in: IncidentHistoryCreate,
        incident_id: int,
        user_id: Optional[int]
    ) -> IncidentHistory:
        """
        Crea una nueva entrada en el historial de cambios de un incidente.
        """
        db_obj = self.model(**obj_in.dict(), incident_id=incident_id, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user(self, db: Session, *, user_id: int, limit: int = 100) -> List[IncidentHistory]:
        """Gets all history entries for a specific user."""
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.timestamp.desc())
            .limit(limit)
            .all()
        )


# --- CRUD para ConversationHistory ---


class CRUDConversationHistory(
    CRUDBase[ConversationHistory, ConversationHistoryCreate, ConversationHistoryCreate]
):
    """
    Clase CRUD para ConversationHistory, conservando métodos existentes.
    """

    def create(
        self, db: Session, *, obj_in: ConversationHistoryCreate, user_id: int
    ) -> ConversationHistory:
        """
        Crea un nuevo mensaje en el historial de una conversación.
        """
        db_obj = self.model(**obj_in.dict(), user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_conversation_id(
        self, db: Session, *, conversation_id: str
    ) -> List[ConversationHistory]:
        """
        Obtiene todos los mensajes de una conversación específica, ordenados por fecha.
        """
        return (
            db.query(self.model)
            .filter(self.model.conversation_id == conversation_id)
            .order_by(self.model.timestamp.asc())
            .all()
        )


incident_history = CRUDIncidentHistory(IncidentHistory)
conversation_history = CRUDConversationHistory(ConversationHistory)
