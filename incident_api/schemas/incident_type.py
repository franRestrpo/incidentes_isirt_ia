"""
Esquemas de Pydantic para los Tipos de Incidentes.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from .incident_category import IncidentCategoryInDB

# --- Esquemas para IncidentType ---


class IncidentTypeBase(BaseModel):
    """Esquema base para los tipos de incidentes."""

    name: str = Field(..., max_length=255, description="Nombre del tipo de incidente.")
    description: Optional[str] = Field(
        None, max_length=512, description="Descripción opcional del tipo."
    )
    incident_category_id: int = Field(
        ..., description="ID de la categoría a la que pertenece."
    )


class IncidentTypeCreate(IncidentTypeBase):
    """Esquema para la creación de un tipo de incidente."""

    pass


class IncidentTypeUpdate(IncidentTypeBase):
    """Esquema para actualizar un tipo de incidente. Todos los campos son opcionales."""

    name: Optional[str] = None
    description: Optional[str] = None
    incident_category_id: Optional[int] = None


class IncidentTypeInDB(IncidentTypeBase):
    """Esquema para devolver la información de un tipo de incidente desde la API."""

    incident_type_id: int = Field(..., description="ID único del tipo de incidente.")
    incident_category: IncidentCategoryInDB = Field(
        ..., description="La categoría de incidente asociada."
    )

    model_config = ConfigDict(from_attributes=True)
