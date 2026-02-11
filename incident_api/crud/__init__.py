"""
Inicialización del módulo CRUD.

Importa instancias de todas las clases CRUD para un acceso centralizado
desde otras partes de la aplicación, como los endpoints de la API.

Ejemplo de uso en un endpoint:
`from incident_api import crud`
`user = crud.user.get(db, id=user_id)`
"""

from .crud_user import user
from .crud_group import group
from .crud_incident import incident
from .crud_incident_log import incident_log
from .crud_audit_log import audit_log
from .crud_history import incident_history, conversation_history
from .crud_evidence_file import evidence_file

# Imports para el seeding y la nueva lógica de incidentes
from .crud_asset_type import asset_type
from .crud_asset import asset
from .crud_attack_vector import attack_vector
from .crud_incident_category import incident_category
from .crud_incident_type import incident_type

# Imports de configuraciones
from .crud_ai_settings import ai_settings, available_ai_model
from .crud_rag_settings import rag_settings
from .crud_task import task
from .crud_knowledge_curation import knowledge_curation


__all__ = [
    "user",
    "group",
    "incident",
    "incident_log",
    "audit_log",
    "incident_history",
    "conversation_history",
    "evidence_file",
    "asset_type",
    "asset",
    "attack_vector",
    "incident_category",
    "incident_type",
    "ai_settings",
    "available_ai_model",
    "rag_settings",
    "task",
    "knowledge_curation",
]
