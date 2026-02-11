"""
Servicio para la lógica de negocio relacionada con las categorías de incidentes.

Este módulo encapsula la lógica de negocio para las operaciones de categorías de incidentes,
actuando como intermediario entre los endpoints de la API y la capa de acceso a datos (CRUD).
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from incident_api import crud, models, schemas


class IncidentCategoryService:
    """
    Clase de servicio para gestionar la lógica de negocio de las categorías de incidentes.
    """

    def get_incident_category_by_id(self, db: Session, incident_category_id: int) -> Optional[models.IncidentCategory]:
        """
        Obtiene una categoría de incidente por su ID.

        Args:
            db: La sesión de la base de datos.
            incident_category_id: El ID de la categoría de incidente a buscar.

        Returns:
            El objeto IncidentCategory o None si no se encuentra.
        """
        return crud.incident_category.get(db, id=incident_category_id)

    def get_all_incident_categories(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[models.IncidentCategory]:
        """
        Obtiene una lista de todas las categorías de incidentes con paginación.
        """
        return crud.incident_category.get_multi(db, skip=skip, limit=limit)

    def create_incident_category(self, db: Session, incident_category_in: schemas.IncidentCategoryCreate) -> models.IncidentCategory:
        """
        Crea una nueva categoría de incidente.
        """
        return crud.incident_category.create(db, obj_in=incident_category_in)


# Crear una instancia del servicio para ser usada en la aplicación
incident_category_service = IncidentCategoryService()