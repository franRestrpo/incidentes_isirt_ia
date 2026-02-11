"""
Servicio para la lógica de negocio relacionada con los vectores de ataque.

Este módulo encapsula la lógica de negocio para las operaciones de vectores de ataque,
actuando como intermediario entre los endpoints de la API y la capa de acceso a datos (CRUD).
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from incident_api import crud, models, schemas


class AttackVectorService:
    """
    Clase de servicio para gestionar la lógica de negocio de los vectores de ataque.
    """

    def get_attack_vector_by_id(self, db: Session, attack_vector_id: int) -> Optional[models.AttackVector]:
        """
        Obtiene un vector de ataque por su ID.

        Args:
            db: La sesión de la base de datos.
            attack_vector_id: El ID del vector de ataque a buscar.

        Returns:
            El objeto AttackVector o None si no se encuentra.
        """
        return crud.attack_vector.get(db, id=attack_vector_id)

    def get_all_attack_vectors(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[models.AttackVector]:
        """
        Obtiene una lista de todos los vectores de ataque con paginación.
        """
        return crud.attack_vector.get_multi(db, skip=skip, limit=limit)

    def create_attack_vector(self, db: Session, attack_vector_in: schemas.AttackVectorCreate) -> models.AttackVector:
        """
        Crea un nuevo vector de ataque.
        """
        return crud.attack_vector.create(db, obj_in=attack_vector_in)


# Crear una instancia del servicio para ser usada en la aplicación
attack_vector_service = AttackVectorService()