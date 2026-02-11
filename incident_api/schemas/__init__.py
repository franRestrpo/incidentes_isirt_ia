"""
Inicialización del módulo de esquemas de Pydantic.

Este archivo importa todos los esquemas para que puedan ser fácilmente importados
desde otras partes de la aplicación, centralizando su acceso.
"""
from pydantic import BaseModel
from typing import Optional

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class TokenPayload(BaseModel):
    sub: str

# --- Nuevos Esquemas Refactorizados ---
from .user import UserBase, UserCreate, UserUpdate, UserInDB
from .evidence_file import EvidenceFileBase, EvidenceFileCreate, EvidenceFileInDB
from .incident_log import (
    IncidentLogBase,
    IncidentLogCreate,
    IncidentLogInDB,
    ManualLogEntryCreate,
)
from .audit_log import AuditLogBase, AuditLogCreate, AuditLogUpdate, AuditLogInDB
from .incident import IncidentBase, IncidentCreate, IncidentUpdate, IncidentInDB, IncidentCreateFromString

# --- Esquemas para la nueva lógica de incidentes ---
from .asset_type import AssetTypeBase, AssetTypeCreate, AssetTypeInDB
from .asset import AssetBase, AssetCreate, AssetUpdate, AssetInDB
from .attack_vector import AttackVectorBase, AttackVectorCreate, AttackVectorInDB
from .incident_category import IncidentCategoryBase, IncidentCategoryCreate, IncidentCategoryInDB
from .incident_type import IncidentTypeBase, IncidentTypeCreate, IncidentTypeUpdate, IncidentTypeInDB

# --- Esquemas Conservados y Refactorizados ---
from .group import GroupBase, GroupCreate, GroupUpdate, GroupInDB
from .ai_settings import (
    AISettingsBase,
    AISettingsCreate,
    AISettingsUpdate,
    AISettingsInDB,
    AvailableAIModelBase,
    AvailableAIModelCreate,
    AvailableAIModelInDB,
)
from .chatbot import (
    ChatbotRequest,
    ChatbotResponse,
    ConversationHistoryBase,
    ConversationHistoryCreate,
    ConversationHistoryInDB,
)
from .incident_history import (
    IncidentHistoryBase,
    IncidentHistoryCreate,
    IncidentHistoryInDB,
)
from .rag_settings import (
    RAGSettingsBase,
    RAGSettingsCreate,
    RAGSettingsUpdate,
    RAGSettingsInDB,
)

from .incident_suggestion import IncidentSuggestionRequest, IncidentSuggestionResponse
from .dialogue_summary import DialogueSummaryRequest, DialogueSummaryResponse
from .task import AsyncTaskResponse, AsyncTaskStatus, TaskBase, TaskCreate, TaskUpdate, TaskInDB
from .ai_analysis import TriageAnalysis, ResponseRecommendations, IncidentEnrichmentResponse, ISIRTAnalysisRequest, SourceFragment, RAGSuggestion
from .knowledge_curation import KnowledgeCuration, KnowledgeCurationCreate, KnowledgeCurationUpdate


__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    # EvidenceFile
    "EvidenceFileBase",
    "EvidenceFileCreate",
    "EvidenceFileInDB",
    # IncidentLog
    "IncidentLogBase",
    "IncidentLogCreate",
    "IncidentLogInDB",
    "ManualLogEntryCreate",
    # AuditLog
    "AuditLogBase",
    "AuditLogCreate",
    "AuditLogUpdate",
    "AuditLogInDB",
    # Incident
    "IncidentBase",
    "IncidentCreate",
    "IncidentUpdate",
    "IncidentInDB",
    "IncidentCreateFromString",
    # AssetType
    "AssetTypeBase",
    "AssetTypeCreate",
    "AssetTypeInDB",
    # Asset
    "AssetBase",
    "AssetCreate",
    "AssetUpdate",
    "AssetInDB",
    # AttackVector
    "AttackVectorBase",
    "AttackVectorCreate",
    "AttackVectorInDB",
    # IncidentCategory
    "IncidentCategoryBase",
    "IncidentCategoryCreate",
    "IncidentCategoryInDB",
    # IncidentType
    "IncidentTypeBase",
    "IncidentTypeCreate",
    "IncidentTypeUpdate",
    "IncidentTypeInDB",
    # Token
    "Token",
    "TokenData",
    "TokenPayload",
    # Group
    "GroupBase",
    "GroupCreate",
    "GroupUpdate",
    "GroupInDB",
    # AI Settings
    "AISettingsBase",
    "AISettingsCreate",
    "AISettingsUpdate",
    "AISettingsInDB",
    "AvailableAIModelBase",
    "AvailableAIModelCreate",
    "AvailableAIModelInDB",
    # Chatbot & Conversation History
    "ChatbotRequest",
    "ChatbotResponse",
    "ConversationHistoryBase",
    "ConversationHistoryCreate",
    "ConversationHistoryInDB",
    # Incident History
    "IncidentHistoryBase",
    "IncidentHistoryCreate",
    "IncidentHistoryInDB",
    # RAG Settings
    "RAGSettingsBase",
    "RAGSettingsCreate",
    "RAGSettingsUpdate",
    "RAGSettingsInDB",
    # Incident Suggestion
    "IncidentSuggestionRequest",
    "IncidentSuggestionResponse",
    # Dialogue Summary
    "DialogueSummaryRequest",
    "DialogueSummaryResponse",
    # Async Task
    "AsyncTaskResponse",
    "AsyncTaskStatus",
    "TaskBase", 
    "TaskCreate", 
    "TaskUpdate", 
    "TaskInDB",
    # AI Analysis
    "TriageAnalysis",
    "ResponseRecommendations",
    "IncidentEnrichmentResponse",
    "ISIRTAnalysisRequest",
    "SourceFragment",
    "RAGSuggestion",
    # Knowledge Curation
    "KnowledgeCuration",
    "KnowledgeCurationCreate",
    "KnowledgeCurationUpdate",
]