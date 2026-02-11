"""
Esquemas de Pydantic para los Vectores de Ataque.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

# --- Esquemas para AttackVector ---


class AttackVectorBase(BaseModel):
    """Esquema base para los vectores de ataque."""

    name: str = Field(..., max_length=255, description="Nombre del vector de ataque.")
    description: Optional[str] = Field(
        None, max_length=512, description="Descripción opcional del vector."
    )


class AttackVectorCreate(AttackVectorBase):
    """Esquema para la creación de un vector de ataque."""

    pass


class AttackVectorInDB(AttackVectorBase):
    """Esquema para devolver la información de un vector de ataque desde la API."""

    attack_vector_id: int = Field(..., description="ID único del vector de ataque.")

    model_config = ConfigDict(from_attributes=True)
