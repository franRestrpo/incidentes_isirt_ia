"""
Esquemas de Pydantic para los Tipos de Activo.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

# --- Esquemas para AssetType ---


class AssetTypeBase(BaseModel):
    """Esquema base para los tipos de activo."""

    name: str = Field(..., max_length=255, description="Nombre del tipo de activo.")
    description: Optional[str] = Field(
        None, max_length=512, description="Descripción opcional del tipo de activo."
    )


class AssetTypeCreate(AssetTypeBase):
    """Esquema para la creación de un tipo de activo."""

    pass


class AssetTypeInDB(AssetTypeBase):
    """Esquema para devolver la información de un tipo de activo desde la API."""

    asset_type_id: int = Field(..., description="ID único del tipo de activo.")

    model_config = ConfigDict(from_attributes=True)
