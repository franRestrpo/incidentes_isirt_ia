"""
Clase base para las operaciones CRUD (Crear, Leer, Actualizar, Eliminar).

Este módulo proporciona una clase genérica `CRUDBase` que puede ser heredada
por las clases de CRUD específicas para cada modelo. Implementa las operaciones
más comunes para reducir la duplicación de código.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from incident_api.db.base import Base

# Definir tipos genéricos para el modelo, esquema de creación y esquema de actualización
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Clase base para operaciones CRUD con tipos genéricos.

    - Modelo de SQLAlchemy.
    - Esquema de creación de Pydantic.
    - Esquema de actualización de Pydantic.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Inicializador de la clase CRUD.

        Args:
            model: El modelo de SQLAlchemy con el que operará esta clase CRUD.
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Obtiene un registro por su ID."""
        # Accede a la clave primaria de forma dinámica
        pk_name = list(self.model.__table__.primary_key.columns)[0].name
        return db.query(self.model).filter(getattr(self.model, pk_name) == id).first()

    def get_by_name(self, db: Session, *, name: str) -> Optional[ModelType]:
        """Obtiene un registro por su campo 'name'."""
        return db.query(self.model).filter(self.model.name == name).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Obtiene múltiples registros con paginación."""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Crea un nuevo registro en la base de datos."""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Actualiza un registro existente."""
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # Usar exclude_unset=True para actualizar solo los campos proporcionados
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """Elimina un registro de la base de datos por su ID."""
        obj = self.get(db, id=id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
