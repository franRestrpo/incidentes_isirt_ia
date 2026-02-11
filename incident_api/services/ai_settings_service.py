"""
Servicio para la lógica de negocio relacionada con la configuración de la IA.

Este módulo gestiona la configuración de los modelos de IA.
"""

import logging
from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status

from incident_api import crud, schemas, models

logger = logging.getLogger(__name__)

def get_active_settings(db: Session) -> models.AIModelSettings:
    """Obtiene la configuración actual del modelo de IA."""
    logger.debug("Obteniendo configuración activa del modelo de IA")
    settings = crud.ai_settings.get_active_settings(db)
    if not settings:
        logger.warning("No se encontró configuración activa del modelo de IA")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La configuración del modelo de IA no ha sido establecida."
        )
    logger.info(f"Configuración de IA obtenida: {settings.model_provider} - {settings.model_name}")
    return settings

def update_settings(
    db: Session,
    settings_in: schemas.AISettingsUpdate
) -> models.AIModelSettings:
    """Actualiza la configuración del modelo de IA."""
    db_settings = get_active_settings(db)
    if not db_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración de IA no encontrada.",
        )
    return crud.ai_settings.update(db, db_obj=db_settings, obj_in=settings_in)

def get_available_models(
    db: Session,
    provider: Optional[str] = None
) -> List[models.AvailableAIModel]:
    """Obtiene la lista de modelos de IA disponibles."""
    return crud.available_ai_model.get_multi_by_provider(db, provider=provider)
