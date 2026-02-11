"""
Servicio para el registro de cambios en incidentes.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from incident_api import crud, schemas
from incident_api.models import Incident, User


class ChangeLoggingService:
    """
    Servicio para manejar el registro de cambios en incidentes.
    """

    def log_changes(
        self,
        db: Session,
        *,
        original_incident: Incident,
        updates: Dict[str, Any],
        user: User,
    ):
        """
        Compara los cambios y crea una entrada en la bitácora para cada uno.
        """
        for field, new_value in updates.items():
            old_value = getattr(original_incident, field)
            if field == 'impact_scores':
                old_dict = old_value or {}
                new_dict = new_value or {}
                if old_dict == new_dict:
                    continue
            elif old_value == new_value:
                continue

            log_entry = schemas.IncidentLogCreate(
                action="Actualización de Campo",
                field_modified=field,
                old_value=str(old_value),
                new_value=str(new_value),
                comments=f"El campo '{field}' fue actualizado por {user.email}.",
            )
            crud.incident_log.create_with_incident_and_user(
                db,
                obj_in=log_entry,
                incident_id=original_incident.incident_id,
                user_id=user.user_id,
            )


change_logging_service = ChangeLoggingService()