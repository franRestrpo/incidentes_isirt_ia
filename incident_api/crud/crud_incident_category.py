"""
Operaciones CRUD para el modelo IncidentCategory.
"""

from incident_api.crud.base import CRUDBase
from incident_api.models.incident_category import IncidentCategory
from incident_api.schemas.incident_category import (
    IncidentCategoryCreate,
    IncidentCategoryCreate,
)


class CRUDIncidentCategory(
    CRUDBase[IncidentCategory, IncidentCategoryCreate, IncidentCategoryCreate]
):
    """Clase CRUD para el modelo IncidentCategory."""

    pass


incident_category = CRUDIncidentCategory(IncidentCategory)
