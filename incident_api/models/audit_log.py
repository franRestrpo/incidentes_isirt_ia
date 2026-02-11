"""
Modelo de la base de datos para el Log de Auditoría General.

Este módulo define el modelo `AuditLog`, que registra todas las acciones
de los usuarios para trazabilidad y auditorías.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, func, JSON
from sqlalchemy.orm import relationship
from incident_api.db.base import Base


class AuditLog(Base):
    """
    Modelo ORM para la tabla `AuditLog`.

    Registra un historial completo de acciones realizadas por usuarios,
    incluyendo login, cambios, accesos, etc., para auditorías y trazabilidad.

    Atributos:
        id (int): Identificador único de la entrada de auditoría.
        user_id (int): ID del usuario que realizó la acción.
        action (str): Tipo de acción realizada (e.g., 'LOGIN', 'UPDATE_USER', 'CREATE_INCIDENT').
        resource_type (str): Tipo de recurso afectado (e.g., 'USER', 'INCIDENT', 'GROUP').
        resource_id (int, opcional): ID del recurso específico afectado.
        details (JSON, opcional): Detalles adicionales de la acción en formato JSON.
        ip_address (str, opcional): Dirección IP desde donde se realizó la acción.
        user_agent (str, opcional): User agent del navegador/dispositivo.
        timestamp (datetime): Fecha y hora en que se registró la acción.
        success (bool): Indica si la acción fue exitosa.

    Relaciones:
        user: Relación con el usuario que realizó la acción.
    """

    __tablename__ = "audit_log"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Identificador único de la entrada de auditoría.",
    )
    user_id = Column(
        Integer,
        ForeignKey("Users.user_id"),
        nullable=True,
        index=True,
        doc="ID del usuario que realizó la acción.",
    )
    action = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Tipo de acción realizada.",
    )
    resource_type = Column(
        String(50),
        nullable=False,
        index=True,
        doc="Tipo de recurso afectado.",
    )
    resource_id = Column(
        Integer,
        nullable=True,
        index=True,
        doc="ID del recurso específico afectado.",
    )
    details = Column(
        JSON,
        nullable=True,
        doc="Detalles adicionales de la acción en formato JSON.",
    )
    ip_address = Column(
        String(45),
        nullable=True,
        doc="Dirección IP desde donde se realizó la acción.",
    )
    user_agent = Column(
        Text,
        nullable=True,
        doc="User agent del navegador/dispositivo.",
    )
    timestamp = Column(
        DateTime,
        server_default=func.now(),
        index=True,
        doc="Fecha y hora del registro de la acción.",
    )
    success = Column(
        Boolean,
        default=True,
        doc="Indica si la acción fue exitosa.",
    )

    # Relación con el usuario
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(user_id='{self.user_id}', action='{self.action}', resource_type='{self.resource_type}')>"