"""
Inicialización del módulo de modelos de la base de datos.

Este archivo importa todos los modelos de SQLAlchemy y las enumeraciones relacionadas
para que puedan ser fácilmente importados desde otras partes de la aplicación.

Facilita el acceso a los modelos, por ejemplo:
`from incident_api.models import User, Incident, Group, AIModelSettings`
"""

# Importar la Base declarativa para que Alembic la descubra
from incident_api.db.base import Base

# --- Nuevos Modelos Refactorizados ---
from .user import User, UserRole
from .incident import Incident, IncidentStatus, IncidentSeverity
from .incident_log import IncidentLog
from .audit_log import AuditLog
from .evidence_file import EvidenceFile
from .asset_type import AssetType
from .asset import Asset
from .incident_category import IncidentCategory
from .incident_type import IncidentType
from .attack_vector import AttackVector


# --- Modelos Conservados ---
from .group import Group
from .ai import AIModelSettings, AvailableAIModel, RAGSettings
from .history import IncidentHistory, ConversationHistory
from .task import Task
from .knowledge_curation import KnowledgeCuration


__all__ = [
    "Base",
    # Nuevos
    "User",
    "UserRole",
    "Incident",
    "IncidentStatus",
    "IncidentSeverity",
    "IncidentLog",
    "AuditLog",
    "EvidenceFile",
    "AssetType",
    "Asset",
    "IncidentCategory",
    "IncidentType",
    "AttackVector",
    # Conservados
    "Group",
    "AIModelSettings",
    "AvailableAIModel",
    "RAGSettings",
    "IncidentHistory",
    "ConversationHistory",
    "Task",
    "KnowledgeCuration",
]