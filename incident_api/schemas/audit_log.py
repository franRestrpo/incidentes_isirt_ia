"""
Esquemas de Pydantic para el modelo AuditLog.

Define los esquemas para la creación, actualización y visualización de registros de auditoría.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AuditLogBase(BaseModel):
    """Esquema base con los campos fundamentales de un registro de auditoría."""

    user_id: int = Field(..., description="ID del usuario que realizó la acción.")
    action: str = Field(..., max_length=100, description="Tipo de acción realizada.")
    resource_type: str = Field(..., max_length=50, description="Tipo de recurso afectado.")
    resource_id: Optional[int] = Field(None, description="ID del recurso específico afectado.")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales en formato JSON.")
    ip_address: Optional[str] = Field(None, max_length=45, description="Dirección IP del cliente.")
    user_agent: Optional[str] = Field(None, description="User agent del navegador/dispositivo.")
    success: bool = Field(True, description="Indica si la acción fue exitosa.")


class AuditLogCreate(AuditLogBase):
    """Esquema para crear un nuevo registro de auditoría."""
    pass


class AuditLogUpdate(BaseModel):
    """Esquema para actualizar un registro de auditoría. Todos los campos son opcionales."""
    details: Optional[Dict[str, Any]] = None
    success: Optional[bool] = None


class AuditLogInDB(AuditLogBase):
    """
    Esquema completo para devolver un registro de auditoría desde la API.
    """

    id: int = Field(..., description="ID único del registro de auditoría.")
    timestamp: datetime = Field(..., description="Fecha y hora del registro.")

    class Config:
        from_attributes = True