"""
Servicio para el manejo del historial de incidentes.
"""

from sqlalchemy.orm import Session
from incident_api import crud, schemas
import logging

logger = logging.getLogger(__name__)


class HistoryService:
    """
    Servicio para manejar el historial de cambios de incidentes.
    """

    def create_incident_history(
        self,
        db: Session,
        incident_id: int,
        user_id: int,
        obj_in: schemas.IncidentHistoryCreate
    ):
        """
        Crea una entrada en el historial de un incidente.
        """
        crud.incident_history.create(
            db,
            obj_in=obj_in,
            incident_id=incident_id,
            user_id=user_id
        )
        logger.debug(f"Entrada de historial creada para incidente {incident_id}")


history_service = HistoryService()