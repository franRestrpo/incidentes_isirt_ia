"""
Endpoints de la API para la gestión de la configuración de RAG.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from incident_api import schemas, models
from incident_api.api import dependencies
from incident_api.services.rag_service import rag_settings_service

router = APIRouter()

@router.get("/", response_model=schemas.RAGSettingsInDB, summary="Obtener configuración de RAG")
def read_rag_settings(
    db: Session = Depends(dependencies.get_db),
    irt_user: models.User = Depends(dependencies.get_current_irt_user),
):
    return rag_settings_service.get_settings(db)

@router.put("/", response_model=schemas.RAGSettingsInDB, summary="Actualizar configuración de RAG")
def update_rag_settings(
    settings_in: schemas.RAGSettingsUpdate,
    db: Session = Depends(dependencies.get_db),
    admin_user: models.User = Depends(dependencies.get_current_admin_user),
):
    return rag_settings_service.update_settings(db, settings_in)
