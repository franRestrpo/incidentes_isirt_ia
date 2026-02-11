"""
Operaciones CRUD para el modelo Asset.
"""

from typing import List
from sqlalchemy.orm import Session
from incident_api.crud.base import CRUDBase
from incident_api.models.asset import Asset
from incident_api.schemas.asset import AssetCreate, AssetUpdate


class CRUDAsset(CRUDBase[Asset, AssetCreate, AssetUpdate]):
    """Clase CRUD para el modelo Asset."""

    def get_multi_by_asset_type(
        self, db: Session, *, asset_type_id: int, skip: int = 0, limit: int = 100
    ) -> List[Asset]:
        return (
            db.query(self.model)
            .filter(self.model.asset_type_id == asset_type_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


asset = CRUDAsset(Asset)
