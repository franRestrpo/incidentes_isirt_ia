"""
Esquemas de Pydantic para el modelo Group.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class GroupBase(BaseModel):
    """Esquema base para los grupos."""

    name: str = Field(..., max_length=100, description="Nombre único del grupo.")
    description: Optional[str] = Field(
        None, max_length=255, description="Descripción del propósito del grupo."
    )


class GroupCreate(GroupBase):
    """Esquema para la creación de un grupo."""

    pass


class GroupUpdate(BaseModel):
    """Esquema para actualizar un grupo. Todos los campos son opcionales."""

    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class GroupInDB(GroupBase):
    """Esquema para devolver un grupo desde la API, incluyendo su ID."""

    id: int = Field(..., description="ID único del grupo.")

    model_config = ConfigDict(from_attributes=True)
