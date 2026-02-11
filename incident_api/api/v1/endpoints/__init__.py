"""
Inicialización del módulo de endpoints de la API v1.

Este archivo importa todos los routers de los endpoints para que puedan ser
registrados en la aplicación principal de FastAPI.
"""

from .login import router as login_router
from .google_auth import router as google_auth_router
from .users import router as users_router
from .groups import router as groups_router
from .incidents import router as incidents_router

from .incident_suggestions import router as incident_suggestions_router
from .ai_settings import router as ai_settings_router
from .chatbot import router as chatbot_router
from .me import router as me_router
from .classification import router as classification_router
from .rag_settings import router as rag_settings_router
from .reporting import router as reporting_router
from .audit import router as audit_router
from .files import router as files_router
from .audit_logs import router as audit_logs_router
from .rag import router as rag_router
from .incident_reports import router as incident_reports_router

__all__ = [
    "login_router",
    "google_auth_router",
    "users_router",
    "groups_router",
    "incidents_router",

    "incident_suggestions_router",
    "ai_settings_router",
    "chatbot_router",
    "me_router",
    "classification_router",
    "rag_settings_router",
    "reporting_router",
    "audit_router",
    "files_router",
    "audit_logs_router",
    "rag_router",
    "incident_reports_router",
]
