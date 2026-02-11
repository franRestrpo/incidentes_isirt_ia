"""
Esquemas de Pydantic para el modelo Incident.

Define los esquemas para la creación, actualización y visualización de incidentes,
manejando la validación de datos y la estructura de las respuestas de la API.
"""

from pydantic import BaseModel, Field, TypeAdapter, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# Importar Enums de los modelos para mantener la consistencia
from incident_api.models.incident import IncidentStatus, IncidentSeverity

# Importar otros esquemas para anidarlos en la respuesta del incidente
from .user import UserInDB
from .group import GroupInDB
from .asset import AssetInDB
from .incident_type import IncidentTypeInDB
from .attack_vector import AttackVectorInDB
from .incident_log import IncidentLogInDB
from .evidence_file import EvidenceFileInDB

# --- Esquemas para Incident ---


class IncidentBase(BaseModel):
    """Esquema base con los campos fundamentales de un incidente."""

    summary: str = Field(
        ..., max_length=255, description="Resumen conciso del incidente."
    )
    description: str = Field(..., description="Descripción detallada del incidente.")
    ai_conversation: Optional[str] = Field(None, description="Registro de la conversación con la IA.")
    discovery_time: datetime = Field(
        ..., description="Fecha y hora en que se descubrió el incidente."
    )
    asset_id: Optional[int] = Field(None, description="ID del activo principal afectado.")
    incident_type_id: Optional[int] = Field(
        None, description="ID del tipo de incidente específico."
    )
    attack_vector_id: Optional[int] = Field(
        None, description="ID del vector de ataque utilizado."
    )
    other_asset_location: Optional[str] = Field(
        None,
        max_length=512,
        description="Descripción del activo si se selecciona 'Otro'.",
    )


class IncidentCreate(IncidentBase):
    """Esquema para crear un nuevo incidente."""

    # reported_by_id se obtendrá del usuario autenticado en el endpoint.
    # ticket_id se generará automáticamente en el backend.
    # Los campos de clasificación (asset_id, incident_type_id, etc.) son opcionales
    # en la creación inicial y pueden ser añadidos después por el equipo de IRT.
    pass


class IncidentUpdate(BaseModel):
    """Esquema para actualizar un incidente. Todos los campos son opcionales."""

    summary: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    ai_conversation: Optional[str] = None
    discovery_time: Optional[datetime] = None
    asset_id: Optional[int] = Field(None, description="ID del nuevo activo afectado.")
    incident_type_id: Optional[int] = Field(
        None, description="ID del nuevo tipo de incidente."
    )
    attack_vector_id: Optional[int] = Field(
        None, description="ID del nuevo vector de ataque."
    )
    other_asset_location: Optional[str] = Field(
        None,
        max_length=512,
        description="Actualización de la descripción del activo 'Otro'.",
    )
    assigned_to_id: Optional[int] = Field(
        None, description="ID del nuevo usuario asignado."
    )
    assigned_to_group_id: Optional[int] = Field(
        None, description="ID del nuevo grupo asignado."
    )
    status: Optional[IncidentStatus] = Field(
        None, description="Nuevo estado del incidente."
    )
    severity: Optional[IncidentSeverity] = Field(
        None, description="Nuevo nivel de severidad."
    )
    root_cause_analysis: Optional[str] = None
    containment_actions: Optional[str] = None
    recovery_actions: Optional[str] = None
    lessons_learned: Optional[str] = None
    corrective_actions: Optional[str] = None
    recommendations: Optional[str] = None
    resolved_at: Optional[datetime] = None

    # --- Impacto ---
    impact_confidentiality: Optional[int] = Field(None, ge=0, le=10)
    impact_integrity: Optional[int] = Field(None, ge=0, le=10)
    impact_availability: Optional[int] = Field(None, ge=0, le=10)
    total_impact: Optional[int] = Field(None, ge=0, le=30)
    


class IncidentInDB(IncidentBase):
    """
    Esquema completo para devolver un incidente desde la API.
    Incluye todos los campos del modelo y anida objetos relacionados para dar un contexto completo.
    """

    incident_id: int = Field(..., description="ID único del incidente.")
    ticket_id: str = Field(..., description="ID de ticket para seguimiento externo.")
    status: IncidentStatus
    severity: Optional[IncidentSeverity] = None
    ai_conversation: Optional[str] = None
    is_active: Optional[bool] = Field(True, description="Indica si el incidente está activo.")
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    # --- Impacto ---
    impact_confidentiality: Optional[int] = 0
    impact_integrity: Optional[int] = 0
    impact_availability: Optional[int] = 0
    total_impact: Optional[int] = 0

    # --- Análisis ISIRT ---
    root_cause_analysis: Optional[str] = None
    containment_actions: Optional[str] = None
    recovery_actions: Optional[str] = None
    lessons_learned: Optional[str] = None
    corrective_actions: Optional[str] = None
    recommendations: Optional[str] = None
    ai_recommendations: Optional[Dict[str, Any]] = None

    # Objetos relacionados anidados para una respuesta rica en contexto
    reporter: UserInDB
    assignee: Optional[UserInDB] = None
    assignee_group: Optional[GroupInDB] = None
    asset: Optional[AssetInDB] = None
    incident_type: Optional[IncidentTypeInDB] = None
    attack_vector: Optional[AttackVectorInDB] = None
    logs: List[IncidentLogInDB] = []
    evidence_files: List[EvidenceFileInDB] = []
    model_config = ConfigDict(from_attributes=True)


# Adaptador para poder parsear IncidentCreate desde un string JSON en un formulario
IncidentCreateFromString = TypeAdapter(IncidentCreate)