"""
Endpoints de la API para la gestión de sugerencias de incidentes.
"""

from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import uuid
import logging
from typing import Dict, Any

from incident_api import schemas, models
from incident_api.api import dependencies
from incident_api.services.incident_analysis_service import incident_analysis_service
from incident_api.services.ai_settings_service import get_active_settings

from incident_api.services.task_service import task_service


router = APIRouter()


async def run_suggestion_analysis(task_id: str, description: str, db: Session):
    """
    Tarea que se ejecuta en segundo plano para obtener sugerencias de la IA.
    """
    try:
        ai_settings = get_active_settings(db)
        suggestions = await incident_analysis_service.get_report_suggestions(
            db=db, description=description, settings=ai_settings
        )
        task = task_service.get_task_by_task_id(db, task_id=task_id)
        task_service.update_task(db, task=task, status="completed", result=suggestions.dict())
    except Exception as e:
        logging.error(f"Error en la tarea de análisis de IA (task: {task_id}): {e}", exc_info=True)
        task = task_service.get_task_by_task_id(db, task_id=task_id)
        task_service.update_task(db, task=task, status="failed", result={"error": str(e)})


@router.post(
    "/request",
    response_model=schemas.AsyncTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Iniciar análisis de IA para sugerencias de incidente",
)
async def get_incident_suggestions(
    request: schemas.IncidentSuggestionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    Inicia un análisis en segundo plano para obtener sugerencias de la IA.

    En lugar de esperar el resultado, devuelve inmediatamente un ID de tarea
    que puede ser usado para consultar el estado y el resultado del análisis.
    """
    task_id = str(uuid.uuid4())
    task_service.create_task(db, task_id=task_id)
    
    background_tasks.add_task(run_suggestion_analysis, task_id, request.description, db)
    
    return {"task_id": task_id, "status": "pending"}


@router.get(
    "/status/{task_id}",
    response_model=schemas.AsyncTaskStatus,
    summary="Consultar estado de un análisis de sugerencias",
)
def get_suggestion_status(task_id: str, db: Session = Depends(dependencies.get_db)):
    """
    Consulta el estado de una tarea de análisis de sugerencias de IA.

    Si la tarea ha finalizado, el campo 'result' contendrá las sugerencias.
    """
    task = task_service.get_task_by_task_id(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    
    return {"task_id": task.task_id, "status": task.status, "result": task.result}
