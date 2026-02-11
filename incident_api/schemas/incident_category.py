"""
Esquemas de Pydantic para las Categorías de Incidentes.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

# --- Esquemas para IncidentCategory ---


class IncidentCategoryBase(BaseModel):
    """Esquema base para las categorías de incidentes."""

    name: str = Field(..., max_length=255, description="Nombre de la categoría.")
    description: Optional[str] = Field(
        None, max_length=512, description="Descripción opcional de la categoría."
    )


class IncidentCategoryCreate(IncidentCategoryBase):
    """Esquema para la creación de una categoría de incidente."""

    pass


class IncidentCategoryInDB(IncidentCategoryBase):
    """Esquema para devolver la información de una categoría desde la API."""

    incident_category_id: int = Field(..., description="ID único de la categoría.")

    model_config = ConfigDict(from_attributes=True)
