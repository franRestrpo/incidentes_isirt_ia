"""
Esquemas de Pydantic para el modelo IncidentLog.

Define los esquemas para la validación y serialización de las entradas de la bitácora
de un incidente, asegurando que los datos de auditoría sean consistentes.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from .user import UserInDB  # Importar para anidar la información del usuario

# --- Esquemas para IncidentLog ---


class IncidentLogBase(BaseModel):
    """Esquema base para una entrada de la bitácora."""

    action: str = Field(
        ...,
        max_length=50,
        description="Acción realizada (e.g., 'Creación', 'Cambio de estado').",
    )
    comments: Optional[str] = Field(
        None, description="Comentarios adicionales sobre la acción."
    )
    field_modified: Optional[str] = Field(
        None, max_length=100, description="Campo del incidente que fue modificado."
    )
    old_value: Optional[str] = Field(
        None, description="Valor del campo antes del cambio."
    )
    new_value: Optional[str] = Field(
        None, description="Valor del campo después del cambio."
    )


class IncidentLogCreate(IncidentLogBase):
    """Esquema para crear una nueva entrada en la bitácora. Los IDs se asignan en el backend."""

    # user_id y incident_id se obtendrán del contexto de la petición (usuario autenticado y recurso)
    pass


class IncidentLogInDB(IncidentLogBase):
    """Esquema para devolver una entrada de la bitácora desde la API."""

    log_id: int = Field(..., description="ID único de la entrada de la bitácora.")
    user_id: int = Field(..., description="ID del usuario que realizó la acción.")
    incident_id: int = Field(..., description="ID del incidente asociado.")
    timestamp: datetime = Field(..., description="Fecha y hora de la acción.")
    user: UserInDB = Field(
        ..., description="Información del usuario que realizó la acción."
    )

    model_config = ConfigDict(from_attributes=True)


class ManualLogEntryCreate(BaseModel):
    """Esquema para una entrada manual en la bitácora."""

    comments: str = Field(..., description="Contenido de la entrada de la bitácora.")
