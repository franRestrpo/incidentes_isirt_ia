"""
Servicio para el manejo de logs de incidentes.
"""

from sqlalchemy.orm import Session
from incident_api import crud, schemas
import logging

logger = logging.getLogger(__name__)


class LogService:
    """
    Servicio para manejar los logs de incidentes.
    """

    def create_incident_log(
        self,
        db: Session,
        incident_id: int,
        user_id: int,
        action: str,
        comments: str
    ):
        """
        Crea una entrada en la bitácora de un incidente.
        """
        log_entry = schemas.IncidentLogCreate(
            action=action,
            comments=comments
        )
        crud.incident_log.create_with_incident_and_user(
            db,
            obj_in=log_entry,
            incident_id=incident_id,
            user_id=user_id,
        )
        logger.debug(f"Entrada de bitácora creada para incidente {incident_id}: {action}")


log_service = LogService()