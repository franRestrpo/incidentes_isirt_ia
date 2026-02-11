"""
Utilidades para la gestión de tipos de incidentes en las pruebas.
"""

from sqlalchemy.orm import Session

from incident_api import crud, schemas
from incident_api.models import IncidentType
from tests.utils.common import random_lower_string


def create_random_incident_type(db: Session, category_id: int) -> IncidentType:
    """
    Crea un tipo de incidente con datos aleatorios para una categoría específica.
    """
    type_in = schemas.IncidentTypeCreate(
        name=f"Type {random_lower_string(6)}",
        description=random_lower_string(30),
        incident_category_id=category_id
    )
    return crud.incident_type.create(db, obj_in=type_in)
