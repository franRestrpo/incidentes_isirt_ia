"""
Endpoints de la API para la gestión de la configuración de IA.
"""

import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from incident_api import schemas, models
from incident_api.api import dependencies
from incident_api.api.decorators import audit_action
from incident_api.services.ai_settings_service import (
    get_active_settings,
    update_settings,
    get_available_models,
)
from incident_api.services.rag_management_service import rag_management_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/", response_model=schemas.AISettingsInDB, summary="Obtener configuración de IA"
)
def read_ai_settings(
    db: Session = Depends(dependencies.get_db),
    irt_user: models.User = Depends(dependencies.get_current_irt_user),
):
    """
    Obtiene la configuración actual del modelo de IA.

    Requiere privilegios de **Miembro IRT**, **Líder IRT** o **Administrador**.

    Args:
        db (Session): Dependencia de la sesión de la base de datos.
        irt_user (models.User): Dependencia que valida los permisos de IRT.

    Returns:
        schemas.AISettingsInDB: La configuración de IA activa.
    """
    settings = get_active_settings(db)
    return settings


@router.put(
    "/", response_model=schemas.AISettingsInDB, summary="Actualizar configuración de IA"
)
@audit_action(action="UPDATE_AI_SETTINGS", resource_type="SYSTEM_CONFIG")
def update_ai_settings_endpoint(
    settings_in: schemas.AISettingsUpdate,
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Actualiza la configuración del modelo de IA.

    Requiere privilegios de **Administrador**.
    Esta acción es auditada.

    Args:
        settings_in (schemas.AISettingsUpdate): La nueva configuración a aplicar.
        request (Request): El objeto de la petición HTTP para la auditoría.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): Dependencia que valida los permisos de Administrador.

    Returns:
        schemas.AISettingsInDB: La configuración de IA actualizada.
    """
    updated_settings = update_settings(db, settings_in)
    return updated_settings


@router.get(
    "/available-models",
    response_model=List[schemas.AvailableAIModelInDB],
    summary="Obtener modelos de IA disponibles",
)
def read_available_ai_models(
    db: Session = Depends(dependencies.get_db),
    provider: Optional[str] = None,
    irt_user: models.User = Depends(dependencies.get_current_irt_user),
):
    """
    Obtiene la lista de modelos de IA disponibles, opcionalmente filtrados por proveedor.

    Requiere privilegios de **Miembro IRT**, **Líder IRT** o **Administrador**.

    Args:
        db (Session): Dependencia de la sesión de la base de datos.
        provider (Optional[str]): Filtro opcional por proveedor (e.g., 'gemini', 'openai').
        irt_user (models.User): Dependencia que valida los permisos de IRT.

    Returns:
        List[schemas.AvailableAIModelInDB]: Lista de modelos de IA disponibles.
    """
    models = get_available_models(db, provider=provider)
    return models


@router.post(
    "/reload-rag",
    response_model=dict,
    summary="Recargar documentos RAG",
)
@audit_action(action="RELOAD_RAG_INDEX", resource_type="SYSTEM_PROCESS")
async def reload_rag_documents(
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Recarga los documentos de playbooks y actualiza el índice FAISS para RAG.

    Esta acción es auditada.

    Requiere privilegios de **Administrador**.

    Args:
        request (Request): El objeto de la petición HTTP para la auditoría.
        db (Session): Sesión de base de datos para operaciones.
        current_user (models.User): Usuario administrador autenticado.

    Returns:
        dict: Respuesta estructurada con el resultado de la operación.
    """
    return await rag_management_service.reload_documents()