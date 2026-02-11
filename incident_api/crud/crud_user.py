"""
Operaciones CRUD para el modelo User.
"""

from typing import Any, Dict, Optional, Union
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from incident_api.core.hashing import Hasher
from incident_api.crud.base import CRUDBase
from incident_api.models.user import User
from incident_api.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    Clase CRUD para el modelo User con métodos específicos.
    """

    def get(self, db: Session, id: Any) -> Optional[User]:
        """Obtiene un usuario por su ID, incluyendo la relación de grupo."""
        pk_name = list(self.model.__table__.primary_key.columns)[0].name
        return (
            db.query(User)
            .options(joinedload(User.group))  # Cargar la relación de grupo
            .filter(getattr(User, pk_name) == id)
            .first()
        )

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Obtiene un usuario por su dirección de correo electrónico, incluyendo la relación de grupo."""
        return (
            db.query(User)
            .options(joinedload(User.group))  # Cargar la relación de grupo
            .filter(User.email == email)
            .first()
        )

    def create(self, db: Session, *, obj_in: Union[UserCreate, Dict[str, Any]]) -> User:
        """
        Crea un nuevo usuario, validando que el email no exista.
        Si se proporciona password, la hashea; si hashed_password, la usa directamente.
        """
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = obj_in.model_dump()

        # Si se proporciona password, hashearla
        if "password" in obj_in_data and obj_in_data["password"]:
            hashed_password = Hasher.get_password_hash(obj_in_data.pop("password"))
            obj_in_data["hashed_password"] = hashed_password

        # Validar que el email no exista
        if self.get_by_email(db, email=obj_in_data["email"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un usuario con este correo electrónico ya existe.",
            )

        # Crear el objeto de modelo
        db_obj = self.model(**obj_in_data)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        """
        Actualiza un usuario. Si se proporciona password, la hashea.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Si se proporciona password, hashearla
        if "password" in update_data and update_data["password"]:
            hashed_password = Hasher.get_password_hash(update_data.pop("password"))
            update_data["hashed_password"] = hashed_password

        # Llamar al método de actualización de la clase base
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def deactivate(self, db: Session, *, db_obj: User) -> User:
        """Desactiva un usuario estableciendo is_active a False."""
        db_obj.is_active = False
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def activate(self, db: Session, *, db_obj: User) -> User:
        """Activa un usuario estableciendo is_active a True."""
        db_obj.is_active = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Obtiene múltiples usuarios con paginación, incluyendo la relación de grupo."""
        return (
            db.query(User)
            .options(joinedload(User.group))  # Cargar la relación de grupo
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_role(self, db: Session, *, roles: list[str]) -> list[User]:
        """Obtiene una lista de usuarios que tienen uno de los roles especificados, incluyendo la relación de grupo."""
        return (
            db.query(User)
            .options(joinedload(User.group))  # Cargar la relación de grupo
            .filter(User.role.in_(roles))
            .all()
        )

    def get_multi_with_filters(
        self, db: Session, *, status: str = None, role: str = None, skip: int = 0, limit: int = 1000
    ) -> list[User]:
        """Obtiene múltiples usuarios con filtros opcionales de estado y rol."""
        query = db.query(User).options(joinedload(User.group))

        if status == "active":
            query = query.filter(User.is_active == True)
        elif status == "inactive":
            query = query.filter(User.is_active == False)

        if role:
            query = query.filter(User.role == role)

        return query.offset(skip).limit(limit).all()


user = CRUDUser(User)