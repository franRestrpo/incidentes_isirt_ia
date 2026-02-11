"""
Enrutador principal de la API.

Este módulo agrega todos los enrutadores de las diferentes versiones y endpoints
de la API en un único APIRouter para ser incluido en la aplicación principal.
"""
from fastapi import APIRouter

from incident_api.api.v1.endpoints import (
    login_router,
    google_auth_router,
    users_router,
    groups_router,
    incidents_router,

    incident_suggestions_router,
    classification_router,
    ai_settings_router,
    rag_settings_router,
    audit_router,
    audit_logs_router,
    files_router,
    me_router,
    reporting_router,
    chatbot_router,
    rag_router,
    incident_reports_router,
)

api_router = APIRouter()

# Incluir todos los routers de los endpoints
api_router.include_router(login_router, prefix="/login", tags=["Login"])
api_router.include_router(google_auth_router, prefix="/login", tags=["Login"])
api_router.include_router(me_router, prefix="/me", tags=["Me"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(groups_router, prefix="/groups", tags=["Groups"])
api_router.include_router(incidents_router, prefix="/incidents", tags=["Incidents"])

api_router.include_router(incident_suggestions_router, prefix="/incident-suggestions", tags=["Incident Suggestions"])
api_router.include_router(classification_router, prefix="/classification", tags=["Classification"])
api_router.include_router(ai_settings_router, prefix="/ai-settings", tags=["AI Settings"])
api_router.include_router(rag_settings_router, prefix="/rag-settings", tags=["RAG Settings"])
api_router.include_router(audit_router, prefix="/audit", tags=["Audit"])
api_router.include_router(audit_logs_router, prefix="/audit-logs", tags=["Audit Logs"])
api_router.include_router(files_router, tags=["Files"])
api_router.include_router(reporting_router, prefix="/reporting", tags=["Reporting"])
api_router.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])
api_router.include_router(rag_router, prefix="/rag", tags=["RAG"])
api_router.include_router(incident_reports_router, prefix="/incident-reports", tags=["Incident Reports"])