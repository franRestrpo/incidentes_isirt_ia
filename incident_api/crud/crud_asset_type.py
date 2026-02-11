"""
Operaciones CRUD para el modelo AssetType.
"""

from incident_api.crud.base import CRUDBase
from incident_api.models.asset_type import AssetType
from incident_api.schemas.asset_type import AssetTypeCreate, AssetTypeCreate


class CRUDAssetType(CRUDBase[AssetType, AssetTypeCreate, AssetTypeCreate]):
    """Clase CRUD para el modelo AssetType."""

    pass


asset_type = CRUDAssetType(AssetType)
