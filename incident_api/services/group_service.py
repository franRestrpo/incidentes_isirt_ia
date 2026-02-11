"""
Servicio para la lógica de negocio relacionada con los grupos.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from incident_api import crud, models, schemas


class GroupService:
    """
    Clase de servicio para gestionar la lógica de negocio de los grupos.
    """

    def get_group_by_id(self, db: Session, group_id: int) -> Optional[models.Group]:
        """Obtiene un grupo por su ID."""
        return crud.group.get(db, id=group_id)

    def get_group_by_name(self, db: Session, name: str) -> Optional[models.Group]:
        """Obtiene un grupo por su nombre."""
        return crud.group.get_by_name(db, name=name)

    def get_all_groups(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[models.Group]:
        """Obtiene una lista de todos los grupos."""
        return crud.group.get_multi(db, skip=skip, limit=limit)

    def create_group(self, db: Session, group_in: schemas.GroupCreate) -> models.Group:
        if crud.group.get_by_name(db, name=group_in.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un grupo con este nombre.",
            )
        return crud.group.create(db, obj_in=group_in)

    def update_group(
        self, db: Session, *, group: models.Group, group_in: schemas.GroupUpdate
    ) -> models.Group:
        """Actualiza un grupo."""
        return crud.group.update(db, db_obj=group, obj_in=group_in)

    def delete_group(self, db: Session, group_id: int) -> Optional[models.Group]:
        """Elimina un grupo."""
        return crud.group.remove(db, id=group_id)


# Instancia del servicio
group_service = GroupService()
