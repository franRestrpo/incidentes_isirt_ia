"""
Servicio para la lógica de negocio relacionada con los tipos de activo.

Este módulo encapsula la lógica de negocio para las operaciones de tipos de activo,
actuando como intermediario entre los endpoints de la API y la capa de acceso a datos (CRUD).
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from incident_api import crud, models, schemas


class AssetTypeService:
    """
    Clase de servicio para gestionar la lógica de negocio de los tipos de activo.
    """

    def get_asset_type_by_id(self, db: Session, asset_type_id: int) -> Optional[models.AssetType]:
        """
        Obtiene un tipo de activo por su ID.

        Args:
            db: La sesión de la base de datos.
            asset_type_id: El ID del tipo de activo a buscar.

        Returns:
            El objeto AssetType o None si no se encuentra.
        """
        return crud.asset_type.get(db, id=asset_type_id)

    def get_all_asset_types(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[models.AssetType]:
        """
        Obtiene una lista de todos los tipos de activo con paginación.
        """
        return crud.asset_type.get_multi(db, skip=skip, limit=limit)

    def create_asset_type(self, db: Session, asset_type_in: schemas.AssetTypeCreate) -> models.AssetType:
        """
        Crea un nuevo tipo de activo.
        """
        return crud.asset_type.create(db, obj_in=asset_type_in)


# Crear una instancia del servicio para ser usada en la aplicación
asset_type_service = AssetTypeService()