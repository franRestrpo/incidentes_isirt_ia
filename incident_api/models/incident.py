"""
Modelo de la base de datos para los Incidentes de Seguridad.

Este módulo define el modelo `Incident`, que representa la tabla `Incidents`.
Es el modelo central del sistema, conteniendo toda la información relevante
de un incidente de seguridad.
"""

import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    DateTime,
    Boolean,
    func,
    JSON,
)
from sqlalchemy.orm import relationship
from incident_api.db.base import Base

# --- Enums Específicos de Incidentes ---


class IncidentStatus(str, enum.Enum):
    """
    Define los estados posibles del ciclo de vida de un incidente.
    """

    NUEVO = "Nuevo"
    INVESTIGANDO = "Investigando"
    CONTENIDO = "Contenido"
    ERRADICADO = "Erradicado"
    RECUPERANDO = "Recuperando"
    RESUELTO = "Resuelto"
    CERRADO = "Cerrado"


class IncidentSeverity(str, enum.Enum):
    """
    Define los niveles de severidad de un incidente, basados en su impacto.
    """

    EVALUAR = "-- Evaluar según matriz --"
    SEV1 = "SEV-1 (Crítico)"
    SEV2 = "SEV-2 (Alto)"
    SEV3 = "SEV-3 (Medio)"
    SEV4 = "SEV-4 (Bajo)"


# --- Modelo Principal de Incidente ---


class Incident(Base):
    """
    Modelo ORM para la tabla `Incidents`.
    """

    __tablename__ = "Incidents"

    # --- Identificadores ---
    incident_id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(20), unique=True, nullable=True, index=True)

    # --- Clasificación y Asignación ---
    reported_by_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("Users.user_id"), nullable=True)
    assigned_to_group_id = Column(Integer, ForeignKey('groups.id'), nullable=True)
    
    asset_id = Column(Integer, ForeignKey("Assets.asset_id"), nullable=True)
    incident_category_id = Column(Integer, ForeignKey('IncidentCategories.incident_category_id'))
    incident_type_id = Column(Integer, ForeignKey("IncidentTypes.incident_type_id"), nullable=True)
    attack_vector_id = Column(Integer, ForeignKey("AttackVectors.attack_vector_id"), nullable=True)
    other_asset_location = Column(String(512), nullable=True)

    # --- Estado y Severidad ---
    status = Column(SQLAlchemyEnum(IncidentStatus), nullable=False, default=IncidentStatus.NUEVO)
    is_active = Column(Boolean, default=True, doc="Indica si el incidente está activo en el sistema.")

# ...

    severity = Column(SQLAlchemyEnum(IncidentSeverity, values_callable=lambda x: [e.value for e in x]), nullable=True)

    # --- Contenido y Descripción ---
    summary = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    ai_conversation = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    ai_recommendations = Column(JSON, nullable=True)

    # --- Análisis Post-Incidente ---
    root_cause_analysis = Column(Text, nullable=True)
    containment_actions = Column(Text, nullable=True)
    recovery_actions = Column(Text, nullable=True)
    lessons_learned = Column(Text, nullable=True)
    corrective_actions = Column(Text, nullable=True)

    # --- Fechas y Tiempos ---
    discovery_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime, nullable=True)

    # --- Impacto ---
    impact_confidentiality = Column(Integer, default=0)
    impact_integrity = Column(Integer, default=0)
    impact_availability = Column(Integer, default=0)
    total_impact = Column(Integer, default=0)

    # --- Relaciones ORM ---
    reporter = relationship("User", foreign_keys=[reported_by_id], back_populates="reported_incidents")
    assignee = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_incidents")
    assignee_group = relationship("Group")
    
    asset = relationship("Asset")
    incident_category = relationship("IncidentCategory")
    incident_type = relationship("IncidentType")
    attack_vector = relationship("AttackVector")

    logs = relationship("IncidentLog", back_populates="incident", cascade="all, delete-orphan")
    evidence_files = relationship("EvidenceFile", back_populates="incident", cascade="all, delete-orphan")
    history = relationship("IncidentHistory", back_populates="incident", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Incident(ticket_id='{self.ticket_id}', summary='{self.summary}')>"