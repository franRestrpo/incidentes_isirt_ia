"""
Servicio para la lógica de negocio relacionada con los incidentes.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from datetime import datetime, timezone

from incident_api import crud, models, schemas
from incident_api.models import User, Incident, IncidentStatus
from incident_api.services.change_logging_service import change_logging_service
from incident_api.services.audit_service import audit_service
from incident_api.api.dependencies import validate_status_change_permission
from incident_api.schemas.graph import GraphNode, GraphEdge
import logging

logger = logging.getLogger(__name__)


class IncidentService:
    """
    Clase de servicio para gestionar la lógica de negocio de los incidentes.
    """

    def get_incident_by_id(
        self, db: Session, incident_id: int
    ) -> Optional[models.Incident]:
        """Obtiene un incidente por su ID."""
        return crud.incident.get(db, id=incident_id)

    def get_all_incidents(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[models.Incident]:
        """Obtiene una lista de todos los incidentes con paginación."""
        return crud.incident.get_multi(db, skip=skip, limit=limit)

    def update_incident(
        self,
        db: Session,
        *,
        incident: models.Incident,
        incident_in: schemas.IncidentUpdate,
        user: models.User,
    ) -> models.Incident:
        """
        Actualiza un incidente, valida permisos y registra cada cambio en la bitácora.
        """
        update_data = incident_in.model_dump(exclude_unset=True)

        # --- Recalcular Impacto Total ---
        if any(key in update_data for key in ['impact_confidentiality', 'impact_integrity', 'impact_availability']):
            conf = update_data.get('impact_confidentiality', incident.impact_confidentiality)
            integ = update_data.get('impact_integrity', incident.impact_integrity)
            avail = update_data.get('impact_availability', incident.impact_availability)
            
            total_impact = (conf or 0) + (integ or 0) + (avail or 0)
            update_data['total_impact'] = total_impact

        if "status" in update_data:
            validate_status_change_permission(
                user, incident, update_data["status"]
            )
            if (
                update_data["status"] == IncidentStatus.CERRADO
                and not incident.resolved_at
            ):
                update_data["resolved_at"] = datetime.now(timezone.utc)

        change_logging_service.log_changes(
            db, original_incident=incident, updates=update_data, user=user
        )

        return crud.incident.update(db, db_obj=incident, obj_in=update_data)


    def add_manual_log_entry(
        self,
        db: Session,
        *,
        incident: models.Incident,
        log_in: schemas.ManualLogEntryCreate,
        user: models.User,
    ) -> models.IncidentLog:
        """Añade una entrada manual a la bitácora de un incidente."""
        log_entry = schemas.IncidentLogCreate(
            action="Entrada Manual", comments=log_in.comments
        )
        return crud.incident_log.create_with_incident_and_user(
            db,
            obj_in=log_entry,
            incident_id=incident.incident_id,
            user_id=user.user_id,
        )

    def deactivate_incident(self, db: Session, incident_id: int, performed_by: Optional[models.User] = None) -> Optional[models.Incident]:
        """Desactiva un incidente (soft delete)."""
        incident = crud.incident.get(db, id=incident_id)
        if not incident:
            return None

        deactivated_incident = crud.incident.deactivate(db, db_obj=incident)

        return deactivated_incident

    def activate_incident(self, db: Session, incident_id: int) -> Optional[models.Incident]:
        """Activa un incidente."""
        incident = crud.incident.get(db, id=incident_id)
        if not incident:
            return None
        return crud.incident.activate(db, db_obj=incident)

    def get_related_entities(self, db: Session, incident_id: int) -> Dict[str, List[Any]]:
        """Obtiene entidades relacionadas a un incidente para expansión del grafo."""
        incident = crud.incident.get(db, id=incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incidente no encontrado")

        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        
        # Añadir nodo para el usuario que reportó (reporter)
        if incident.reporter:
            nodes.append(GraphNode(
                id=f"user-{incident.reporter.user_id}",
                data={"label": f"Reportado por: {incident.reporter.full_name}", "type": "user"}
            ))
            edges.append(GraphEdge(
                id=f"e-incident-{incident_id}-reporter-{incident.reporter.user_id}",
                source=f"incident-{incident_id}",
                target=f"user-{incident.reporter.user_id}",
                label="reportado por"
            ))

        # Añadir nodo para el usuario asignado (assignee)
        if incident.assignee:
            nodes.append(GraphNode(
                id=f"user-{incident.assignee.user_id}",
                data={"label": f"Asignado a: {incident.assignee.full_name}", "type": "user"},
                position={"x": 500, "y": 400} # Posición relativa
            ))
            edges.append(GraphEdge(
                id=f"e-incident-{incident_id}-assignee-{incident.assignee.user_id}",
                source=f"incident-{incident_id}",
                target=f"user-{incident.assignee.user_id}",
                label="asignado a"
            ))

        return {"nodes": nodes, "edges": edges}


incident_service = IncidentService()
