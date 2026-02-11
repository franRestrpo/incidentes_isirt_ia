"""
Modelo de la base de datos para el Usuario.

Este módulo define el modelo `User`, que representa la tabla `Users` en la base de datos.
Contiene la estructura y las relaciones de los usuarios del sistema.
"""

import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum as SQLAlchemyEnum,
    DateTime,
    ForeignKey,
    Boolean,
    func,
)
from sqlalchemy.orm import relationship
from incident_api.db.base import Base


class UserRole(str, enum.Enum):
    """
    Define los roles que puede tener un usuario en el sistema.
    Estos roles determinan los permisos y el acceso a diferentes funcionalidades.
    """

    EMPLEADO = "Empleado"
    MIEMBRO_IRT = "Miembro IRT"
    LIDER_IRT = "Líder IRT"
    ADMINISTRADOR = "Administrador"
    SUPER_ADMIN = "Super Admin"


class User(Base):
    """
    Modelo ORM para la tabla `Users`.

    Atributos:
        user_id (int): Identificador único del usuario.
        email (str): Correo electrónico del usuario, debe ser único.
        full_name (str): Nombre completo del usuario.
        role (UserRole): Rol del usuario dentro del sistema.
        created_at (datetime): Fecha y hora de creación del registro.
        hashed_password (str): Contraseña del usuario almacenada de forma segura.
        position (str, opcional): Cargo o puesto del usuario.
        city (str, opcional): Ciudad de ubicación del usuario.
        is_active (bool): Indica si la cuenta del usuario está activa.
        group_id (int, opcional): ID del grupo al que pertenece el usuario.

    Relaciones:
        group: Relación con el modelo `Group`.
        reported_incidents: Incidentes reportados por este usuario.
        assigned_incidents: Incidentes asignados a este usuario.
        logs: Entradas de bitácora creadas por este usuario.
        uploaded_files: Archivos de evidencia subidos por este usuario.
    """

    __tablename__ = "Users"

    user_id = Column(
        Integer, primary_key=True, index=True, doc="Identificador único del usuario."
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Correo electrónico del usuario, usado para el login.",
    )
    full_name = Column(String(255), nullable=False, doc="Nombre completo del usuario.")
    role = Column(
        SQLAlchemyEnum(UserRole),
        nullable=False,
        default=UserRole.EMPLEADO,
        doc="Rol del usuario que define sus permisos.",
    )
    created_at = Column(
        DateTime, server_default=func.now(), doc="Fecha y hora de creación del usuario."
    )
    hashed_password = Column(
        String(255), nullable=True, doc="Contraseña hasheada del usuario (NULL para usuarios OAuth)."
    )
    position = Column(
        String(100), nullable=True, doc="Cargo que ocupa el usuario en la organización."
    )
    city = Column(
        String(100), nullable=True, doc="Ciudad donde se encuentra el usuario."
    )
    is_active = Column(
        Boolean, default=True, doc="Indica si el usuario está activo en el sistema."
    )
    group_id = Column(
        Integer,
        ForeignKey("groups.id"),
        nullable=True,
        doc="ID del grupo de respuesta a incidentes al que pertenece.",
    )

    # Relación con la tabla de grupos (si aplica)
    group = relationship("Group", back_populates="users")

    # Relaciones inversas para acceder a los incidentes y logs desde el usuario
    reported_incidents = relationship(
        "Incident", back_populates="reporter", foreign_keys="[Incident.reported_by_id]"
    )
    assigned_incidents = relationship(
        "Incident", back_populates="assignee", foreign_keys="[Incident.assigned_to_id]"
    )
    logs = relationship("IncidentLog", back_populates="user")
    uploaded_files = relationship("EvidenceFile", back_populates="uploader")

    # Relaciones con los historiales
    incident_history = relationship("IncidentHistory", back_populates="user")
    conversation_history = relationship("ConversationHistory", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
