"""
Esquemas de Pydantic para el modelo IncidentHistory.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from .user import UserInDB


class IncidentHistoryBase(BaseModel):
    """Esquema base para el historial de cambios de un incidente."""

    field_changed: str = Field(
        ..., description="El campo del incidente que fue modificado."
    )
    old_value: Optional[str] = Field(None, description="Valor anterior del campo.")
    new_value: Optional[str] = Field(None, description="Valor nuevo del campo.")
    details: Optional[str] = Field(
        None, description="Detalles adicionales sobre el cambio."
    )


class IncidentHistoryCreate(IncidentHistoryBase):
    """Esquema para crear una nueva entrada de historial. Los IDs se asignan en el backend."""

    # incident_id y user_id se gestionan en el servicio que realiza el cambio.
    pass


class IncidentHistoryInDB(IncidentHistoryBase):
    """Esquema para devolver una entrada de historial desde la API."""

    id: int
    incident_id: int
    timestamp: datetime
    user: Optional[UserInDB] = Field(
        None, description="Usuario que realizó el cambio (si aplica)."
    )

    model_config = ConfigDict(from_attributes=True)
