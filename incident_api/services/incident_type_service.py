"""
Servicio para la lógica de negocio relacionada con los tipos de incidentes.

Este módulo encapsula la lógica de negocio para las operaciones de tipos de incidentes,
actuando como intermediario entre los endpoints de la API y la capa de acceso a datos (CRUD).
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from incident_api import crud, models, schemas


class IncidentTypeService:
    """
    Clase de servicio para gestionar la lógica de negocio de los tipos de incidentes.
    """

    def get_incident_type_by_id(self, db: Session, incident_type_id: int) -> Optional[models.IncidentType]:
        """
        Obtiene un tipo de incidente por su ID.

        Args:
            db: La sesión de la base de datos.
            incident_type_id: El ID del tipo de incidente a buscar.

        Returns:
            El objeto IncidentType o None si no se encuentra.
        """
        return crud.incident_type.get(db, id=incident_type_id)

    def get_incident_types(
        self, db: Session, skip: int = 0, limit: int = 100, incident_category_id: Optional[int] = None
    ) -> List[models.IncidentType]:
        """
        Obtiene una lista de todos los tipos de incidentes con paginación y filtro opcional.
        """
        if incident_category_id:
            return crud.incident_type.get_multi_by_incident_category(db, incident_category_id=incident_category_id, skip=skip, limit=limit)
        return crud.incident_type.get_multi(db, skip=skip, limit=limit)

    def create_incident_type(self, db: Session, incident_type_in: schemas.IncidentTypeCreate) -> models.IncidentType:
        """
        Crea un nuevo tipo de incidente.
        """
        return crud.incident_type.create(db, obj_in=incident_type_in)


# Crear una instancia del servicio para ser usada en la aplicación
incident_type_service = IncidentTypeService()