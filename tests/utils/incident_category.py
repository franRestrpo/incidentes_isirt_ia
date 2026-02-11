"""
Utilidades para la gestión de categorías de incidentes en las pruebas.
"""

from sqlalchemy.orm import Session

from incident_api import crud, schemas
from incident_api.models import IncidentCategory
from tests.utils.common import random_lower_string


def create_random_incident_category(db: Session) -> IncidentCategory:
    """
    Crea una categoría de incidente con datos aleatorios.
    """
    category_in = schemas.IncidentCategoryCreate(
        name=f"Category {random_lower_string(6)}",
        description=random_lower_string(30)
    )
    return crud.incident_category.create(db, obj_in=category_in)
