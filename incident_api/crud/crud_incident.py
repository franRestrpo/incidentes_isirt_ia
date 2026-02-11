"""
Operaciones CRUD para el modelo Incident.
"""

from typing import Any, Dict, List, Union

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone
from sqlalchemy import case

from incident_api.crud.base import CRUDBase
from incident_api.models.incident import Incident, IncidentStatus
from incident_api.models.incident_type import IncidentType
from incident_api.schemas.incident import IncidentCreate, IncidentUpdate


class CRUDIncident(CRUDBase[Incident, IncidentCreate, IncidentUpdate]):
    """
    Clase CRUD para el modelo Incident con métodos específicos.
    """

    def create(
        self, db: Session, *, obj_in: IncidentCreate, reported_by_id: int
    ) -> Incident:
        """
        Crea un nuevo incidente, asignando un ticket_id único después de la creación inicial.
        """
        # Convertir el esquema Pydantic a un diccionario
        obj_in_data = obj_in.model_dump()
        
        # Crear el objeto del modelo sin el ticket_id
        db_obj = self.model(
            **obj_in_data, reported_by_id=reported_by_id
        )

        db.add(db_obj)
        db.flush()  # Asigna el ID sin hacer commit

        # Generar el ticket_id usando el ID ya asignado por la BD
        current_year = db_obj.created_at.year
        db_obj.ticket_id = f"INC-{current_year}-{db_obj.incident_id:04d}"
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Incident,
        obj_in: Union[IncidentUpdate, Dict[str, Any]]
    ) -> Incident:
        """
        Actualiza un incidente existente con los datos proporcionados.

        Args:
            db: Sesión de base de datos.
            db_obj: Instancia del incidente a actualizar.
            obj_in: Datos de actualización, ya sea un esquema IncidentUpdate o un diccionario.

        Returns:
            El incidente actualizado.
        """
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def deactivate(self, db: Session, *, db_obj: Incident) -> Incident:
        """Desactiva un incidente estableciendo is_active a False."""
        db_obj.is_active = False
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def activate(self, db: Session, *, db_obj: Incident) -> Incident:
        """Activa un incidente estableciendo is_active a True."""
        db_obj.is_active = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def count_by_reporter(self, db: Session, *, user_id: int) -> int:
        """Counts the total number of incidents reported by a user."""
        return db.query(self.model).filter(self.model.reported_by_id == user_id).count()

    def count_resolved_by_assignee(self, db: Session, *, user_id: int) -> int:
        """Counts resolved or closed incidents assigned to a user."""
        return (
            db.query(self.model)
            .filter(self.model.assigned_to_id == user_id)
            .filter(
                self.model.status.in_([IncidentStatus.RESUELTO, IncidentStatus.CERRADO])
            )
            .count()
        )

    def count_assigned_to_user(self, db: Session, *, user_id: int) -> int:
        """Counts the total number of incidents assigned to a user."""
        return db.query(self.model).filter(self.model.assigned_to_id == user_id).count()

    def get_average_resolution_time_by_assignee(self, db: Session, *, user_id: int) -> float | None:
        """Calculates the average resolution time in hours for incidents assigned to a user."""
        from sqlalchemy import extract
        result = db.query(
            func.avg(
                extract('epoch', self.model.updated_at - self.model.created_at) / 3600
            )
        ).filter(
            self.model.assigned_to_id == user_id,
            self.model.status.in_([IncidentStatus.RESUELTO, IncidentStatus.CERRADO]),
            self.model.updated_at.isnot(None)
        ).scalar()
        return result

    def get_incidents_by_status_for_user(self, db: Session, *, user_id: int) -> dict[str, int]:
        """Gets a count of incidents by status for incidents reported or assigned to a user."""
        results = db.query(
            self.model.status,
            func.count(self.model.incident_id)
        ).filter(
            (self.model.reported_by_id == user_id) | (self.model.assigned_to_id == user_id)
        ).group_by(self.model.status).all()
        return {status.value: count for status, count in results}

    def get_top_incident_types_by_user(
        self, db: Session, *, user_id: int, limit: int = 3
    ) -> List[str]:
        """
        Gets the names of the most common incident types a user has worked on
        (either reported or assigned).
        """
        # Incidents reported by the user
        reported = (
            db.query(self.model.incident_type_id, func.count(self.model.incident_id).label('count'))
            .filter(self.model.reported_by_id == user_id)
            .group_by(self.model.incident_type_id)
        )

        # Incidents assigned to the user
        assigned = (
            db.query(self.model.incident_type_id, func.count(self.model.incident_id).label('count'))
            .filter(self.model.assigned_to_id == user_id)
            .group_by(self.model.incident_type_id)
        )

        # It's complex to do a proper UNION and aggregation in one go with SQLAlchemy Core,
        # so we'll handle this in Python for simplicity, which is acceptable for metrics.

        type_counts = {}
        for type_id, count in reported.all() + assigned.all():
            if type_id:
                type_counts[type_id] = type_counts.get(type_id, 0) + count

        # Get the top N type_ids
        top_type_ids = sorted(type_counts, key=type_counts.get, reverse=True)[:limit]

        if not top_type_ids:
            return []

        ordering = case(
            {type_id: index for index, type_id in enumerate(top_type_ids)},
            value=IncidentType.incident_type_id,
        )

        # Get the names of the top types, ordered by frequency
        top_types = (
            db.query(IncidentType.name)
            .filter(IncidentType.incident_type_id.in_(top_type_ids))
            .order_by(ordering)
            .all()
        )

        return [name for (name,) in top_types]

    def get_multi_by_user_association(self, db: Session, *, user_id: int) -> List[Incident]:
        """Gets all incidents a user is associated with (reported or assigned)."""
        return (
            db.query(self.model)
            .options(joinedload(self.model.reporter), joinedload(self.model.assignee))
            .filter(
                or_(self.model.reported_by_id == user_id, self.model.assigned_to_id == user_id)
            )
            .order_by(self.model.created_at.desc())
            .all()
        )


incident = CRUDIncident(Incident)
