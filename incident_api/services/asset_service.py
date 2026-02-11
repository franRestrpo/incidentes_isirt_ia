"""
Servicio para la lógica de negocio relacionada con los activos.

Este módulo encapsula la lógica de negocio para las operaciones de activos,
actuando como intermediario entre los endpoints de la API y la capa de acceso a datos (CRUD).
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from incident_api import crud, models, schemas


class AssetService:
    """
    Clase de servicio para gestionar la lógica de negocio de los activos.
    """

    def get_asset_by_id(self, db: Session, asset_id: int) -> Optional[models.Asset]:
        """
        Obtiene un activo por su ID.

        Args:
            db: La sesión de la base de datos.
            asset_id: El ID del activo a buscar.

        Returns:
            El objeto Asset o None si no se encuentra.
        """
        return crud.asset.get(db, id=asset_id)

    def get_assets(
        self, db: Session, skip: int = 0, limit: int = 100, asset_type_id: Optional[int] = None
    ) -> List[models.Asset]:
        """
        Obtiene una lista de todos los activos con paginación y filtro opcional.
        """
        if asset_type_id:
            return crud.asset.get_multi_by_asset_type(db, asset_type_id=asset_type_id, skip=skip, limit=limit)
        return crud.asset.get_multi(db, skip=skip, limit=limit)

    def create_asset(self, db: Session, asset_in: schemas.AssetCreate) -> models.Asset:
        """
        Crea un nuevo activo.
        """
        return crud.asset.create(db, obj_in=asset_in)


# Crear una instancia del servicio para ser usada en la aplicación
asset_service = AssetService()