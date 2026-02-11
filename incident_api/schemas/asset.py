"""
Esquemas de Pydantic para los Activos.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from .asset_type import AssetTypeInDB

# --- Esquemas para Asset ---


class AssetBase(BaseModel):
    """Esquema base para los activos."""

    name: str = Field(..., max_length=255, description="Nombre del activo.")
    description: Optional[str] = Field(
        None, max_length=512, description="Descripción opcional del activo."
    )
    asset_type_id: int = Field(..., description="ID del tipo de activo al que pertenece.")


class AssetCreate(AssetBase):
    """Esquema para la creación de un activo."""

    pass


class AssetUpdate(AssetBase):
    """Esquema para actualizar un activo. Todos los campos son opcionales."""

    name: Optional[str] = None
    description: Optional[str] = None
    asset_type_id: Optional[int] = None


class AssetInDB(AssetBase):
    """Esquema para devolver la información de un activo desde la API."""

    asset_id: int = Field(..., description="ID único del activo.")
    asset_type: AssetTypeInDB = Field(..., description="El tipo de activo asociado.")

    model_config = ConfigDict(from_attributes=True)
