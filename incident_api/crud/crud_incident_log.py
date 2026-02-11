"""Operaciones CRUD para el modelo IncidentLog."""

from sqlalchemy.orm import Session
from typing import List

from incident_api.crud.base import CRUDBase
from incident_api.models.incident_log import IncidentLog
from incident_api.schemas.incident_log import IncidentLogCreate


class CRUDIncidentLog(
    CRUDBase[IncidentLog, IncidentLogCreate, IncidentLogCreate]
):  # Update schema is same as create
    """Clase CRUD para el modelo IncidentLog."""

    def create_with_incident_and_user(
        self, db: Session, *, obj_in: IncidentLogCreate, incident_id: int, user_id: int
    ) -> IncidentLog:
        """
        Crea un nuevo registro de log asociado a un incidente y un usuario.
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data, incident_id=incident_id, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_incident(self, db: Session, *, incident_id: int) -> List[IncidentLog]:
        """
        Obtiene todos los registros de log para un incidente específico.
        """
        return (
            db.query(self.model)
            .filter(self.model.incident_id == incident_id)
            .order_by(self.model.timestamp.asc())
            .all()
        )
    def get_by_user(self, db: Session, *, user_id: int, limit: int = 100) -> List[IncidentLog]:
        """Gets all log entries for a specific user."""
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.timestamp.desc())
            .limit(limit)
            .all()
        )

    def count_comments_by_user(self, db: Session, *, user_id: int) -> int:
        """Counts the number of comments made by a user in incident logs."""
        return db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.comments.isnot(None),
            self.model.comments != ''
        ).count()


incident_log = CRUDIncidentLog(IncidentLog)
