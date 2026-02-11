"""
Operaciones CRUD para el modelo IncidentType.
"""

from typing import List
from sqlalchemy.orm import Session
from incident_api.crud.base import CRUDBase
from incident_api.models.incident_type import IncidentType
from incident_api.schemas.incident_type import IncidentTypeCreate, IncidentTypeUpdate


class CRUDIncidentType(CRUDBase[IncidentType, IncidentTypeCreate, IncidentTypeUpdate]):
    """Clase CRUD para el modelo IncidentType."""

    def get_multi_by_incident_category(
        self, db: Session, *, incident_category_id: int, skip: int = 0, limit: int = 100
    ) -> List[IncidentType]:
        return (
            db.query(self.model)
            .filter(self.model.incident_category_id == incident_category_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


incident_type = CRUDIncidentType(IncidentType)
