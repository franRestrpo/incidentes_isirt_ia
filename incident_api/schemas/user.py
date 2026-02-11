"""
Esquemas de Pydantic para el modelo User.

Este módulo define los esquemas de Pydantic utilizados para la validación de datos
y la serialización/deserialización de objetos User en la API.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from incident_api.models.user import UserRole  # Importar el Enum del modelo
from .group import GroupInDB as GroupSchema

# --- Esquemas para User ---


class UserBase(BaseModel):
    """Esquema base con los campos comunes de un usuario."""

    email: EmailStr = Field(..., description="Correo electrónico del usuario.")
    full_name: str = Field(
        ..., min_length=3, max_length=255, description="Nombre completo del usuario."
    )
    role: UserRole = Field(
        default=UserRole.EMPLEADO, description="Rol del usuario en el sistema."
    )
    position: Optional[str] = Field(
        None, max_length=100, description="Cargo del usuario."
    )
    city: Optional[str] = Field(None, max_length=100, description="Ciudad del usuario.")
    is_active: bool = Field(True, description="Indica si el usuario está activo.")
    group_id: Optional[int] = Field(
        None, description="ID del grupo al que pertenece el usuario."
    )


class UserCreate(UserBase):
    """Esquema para la creación de un nuevo usuario. La contraseña es opcional (para OAuth)."""

    password: Optional[str] = Field(
        None, min_length=8, description="Contraseña para el nuevo usuario (opcional para OAuth)."
    )


class UserUpdate(BaseModel):
    """Esquema para actualizar un usuario existente. Todos los campos son opcionales."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=3, max_length=255)
    role: Optional[UserRole] = None
    position: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    group_id: Optional[int] = None
    password: Optional[str] = Field(
        None, min_length=8, description="Nueva contraseña (si se desea cambiar)."
    )


from .group import GroupInDB as GroupSchema

class UserInDB(UserBase):
    """Esquema para representar un usuario tal como se devuelve desde la API."""

    user_id: int = Field(..., description="ID único del usuario.")
    created_at: datetime = Field(
        ..., description="Fecha y hora de creación del usuario."
    )
    group: Optional[GroupSchema] = Field(None, description="Grupo al que pertenece el usuario.")

    model_config = ConfigDict(
        from_attributes=True,  # Permite la serialización desde el modelo ORM
        json_encoders={datetime: lambda v: v.isoformat()}
    )
