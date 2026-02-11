"""
Endpoints de la API para la gestión de incidentes de seguridad.
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, BackgroundTasks, Request
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os

# Almacenamiento en memoria para los resultados de las tareas.
# En producción, usar una solución más robusta como Redis o una tabla en la BD.
task_results: Dict[str, Any] = {}

# Importar el nuevo TypeAdapter y los settings
from incident_api import schemas, models, crud
from incident_api.schemas import IncidentCreateFromString
from incident_api.schemas.graph import RelatedEntitiesResponse
from incident_api.core.config import settings
from incident_api.api import dependencies
from incident_api.api.decorators import audit_action
from incident_api.services.incident_service import incident_service
from incident_api.services.incident_creation_service import IncidentCreationService
from incident_api.services.incident_analysis_service import incident_analysis_service
from incident_api.services.isirt_analysis_service import isirt_analysis_service
from incident_api.services.dialogue_service import dialogue_service
from incident_api.services.ai_settings_service import get_active_settings
from incident_api.models import UserRole
from incident_api.services.incident_triage_service import incident_triage_service
from incident_api.services import report_service


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/",
    response_model=schemas.IncidentInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo incidente",
)
@audit_action(action="CREATE_INCIDENT", resource_type="INCIDENT")
async def create_incident(
    request: Request,
    incident_data: str = Form(...),
    evidence_files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
    creation_service: IncidentCreationService = Depends(dependencies.get_incident_creation_service),
):
    """
    Crea un nuevo incidente de seguridad, incluyendo archivos de evidencia.

    El usuario que reporta el incidente es el usuario actualmente autenticado.
    Esta acción es auditada.

    Args:
        request (Request): El objeto de la petición HTTP para la auditoría.
        incident_data (str): Un string JSON con los datos del incidente.
        evidence_files (Optional[List[UploadFile]]): Lista de archivos de evidencia.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): Dependencia que obtiene el usuario autenticado.
        creation_service (IncidentCreationService): Dependencia del servicio de creación.

    Returns:
        schemas.IncidentInDB: El incidente recién creado.
    """
    try:
        new_incident = await creation_service.create_incident_from_json_string(
            db=db,
            incident_data_str=incident_data,
            user=current_user,
            evidence_files=evidence_files,
        )

        logger.info(f"Incidente creado exitosamente - ID: {new_incident.incident_id}, Ticket: {new_incident.ticket_id}, Usuario: {current_user.user_id}")
        return new_incident

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error al crear incidente - Usuario: {current_user.user_id}, Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error inesperado al crear el incidente."
        )


@router.get(
    "/",
    response_model=List[schemas.IncidentInDB],
    summary="Obtener todos los incidentes",
)
def read_incidents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(dependencies.get_db),
    irt_user: models.User = Depends(dependencies.get_current_irt_user),
):
    """
    Obtiene una lista de todos los incidentes de seguridad.

    Requiere que el usuario actual sea un **Miembro IRT**, **Líder IRT** o **Administrador**.

    Args:
        skip (int): Número de incidentes a omitir para paginación.
        limit (int): Número máximo de incidentes a devolver.
        db (Session): Dependencia de la sesión de la base de datos.
        irt_user (models.User): Dependencia que valida que el usuario tiene rol de IRT.

    Returns:
        List[schemas.IncidentInDB]: Una lista de objetos de incidentes.
    """
    incidents = incident_service.get_all_incidents(db, skip=skip, limit=limit)
    return incidents


@router.get(
    "/{incident_id}",
    response_model=schemas.IncidentInDB,
    summary="Obtener incidente por ID",
)
def read_incident(
    incident: models.Incident = Depends(dependencies.get_incident_with_permission),
):
    """
    Obtiene los detalles de un incidente específico por su ID.
    """
    return incident


@router.get(
    "/{incident_id}/related-entities",
    response_model=RelatedEntitiesResponse,
    summary="Obtener entidades relacionadas para el grafo de auditoría",
)
def get_related_entities(
    incident_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_irt_user),
):
    """
    Obtiene una lista de nodos y aristas relacionadas a un incidente para
    poder expandir dinámicamente el grafo de auditoría en el frontend.

    Requiere privilegios de **Miembro IRT**, **Líder IRT** o **Administrador**.

    Args:
        incident_id (int): ID del incidente a expandir.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): Dependencia que valida el rol de IRT.

    Returns:
        RelatedEntitiesResponse: Un objeto con listas de nodos y aristas para el grafo.
    """
    return incident_service.get_related_entities(db, incident_id=incident_id)


@router.put(
    "/{incident_id}",
    response_model=schemas.IncidentInDB,
    summary="Actualizar incidente",
)
@audit_action(action="UPDATE_INCIDENT", resource_type="INCIDENT", resource_id_param="incident_id", get_resource_func=crud.incident.get)
def update_incident(
    incident_id: int,
    request: Request,
    incident_update: schemas.IncidentUpdate,
    incident: models.Incident = Depends(dependencies.get_incident_with_permission),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    Actualiza la información de un incidente existente.

    Valida que el usuario actual sea el reportante, el asignado, o un miembro del IRT.
    Esta acción es auditada con detalle de cambios.

    Args:
        incident_id (int): ID del incidente a actualizar.
        request (Request): El objeto de la petición HTTP para la auditoría.
        incident_update (schemas.IncidentUpdate): Datos a actualizar.
        incident (models.Incident): Dependencia que obtiene el incidente y valida permisos.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): Dependencia que obtiene el usuario autenticado.

    Returns:
        schemas.IncidentInDB: El incidente actualizado.
    """
    updated_incident = incident_service.update_incident(
        db, incident=incident, incident_in=incident_update, user=current_user
    )
    return updated_incident


@router.post(
    "/{incident_id}/triage",
    response_model=Dict[str, Any],
    summary="Realizar triage inicial de un incidente",
)
async def perform_incident_triage(
    incident: models.Incident = Depends(dependencies.get_incident_with_permission),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_irt_user),
):
    """
    Realiza el triage inicial de un incidente utilizando el servicio de triage.

    Requiere que el usuario actual sea un **Miembro IRT**, **Líder IRT** o **Administrador**.

    Args:
        incident (models.Incident): Dependencia que obtiene el incidente y valida permisos.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): Dependencia que valida que el usuario tiene rol de IRT.

    Returns:
        Dict[str, Any]: El resultado del triage.
    """
    try:
        triage_result = await incident_triage_service.perform_initial_triage(db, incident)
        return triage_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error realizando el triage del incidente: {str(e)}",
        )


@router.post(
    "/{incident_id}/isirt-analysis",
    response_model=Dict[str, Any],
    summary="Generar análisis ISIRT de un incidente",
)
@audit_action(action="GENERATE_ISIRT_ANALYSIS", resource_type="INCIDENT", resource_id_param="incident_id")
async def generate_isirt_analysis(
    request: Request,
    incident: models.Incident = Depends(dependencies.get_incident_with_permission),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_irt_user),
):
    """
    Genera un análisis ISIRT detallado y enriquecido con RAG para un incidente.

    Requiere que el usuario actual sea un **Miembro IRT**, **Líder IRT** o **Administrador**.
    """
    try:
        ai_settings = get_active_settings(db)
        if not ai_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay una configuración de IA activa."
            )

        # Llama al nuevo servicio que incluye la lógica de RAG
        analysis_result = await incident_analysis_service.get_incident_enrichment(
            db, incident=incident, settings=ai_settings
        )

        if not analysis_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="El análisis de IA no devolvió ningún resultado."
            )

        # Actualizar el incidente con las recomendaciones de la IA
        crud.incident.update(db, db_obj=incident, obj_in={"ai_recommendations": analysis_result})
        
        # Devolver el resultado para que el frontend lo muestre inmediatamente
        return analysis_result

    except Exception as e:
        logger.error(f"Error generando el análisis ISIRT para el incidente {incident.incident_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando el análisis ISIRT del incidente: {str(e)}",
        )


@router.post(
    "/{incident_id}/logs",
    response_model=schemas.IncidentLogInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Añadir entrada manual a la bitácora",
)
@audit_action(action="ADD_INCIDENT_LOG", resource_type="INCIDENT", resource_id_param="incident_id")
def add_manual_log_entry(
    incident_id: int,
    request: Request,
    log_in: schemas.ManualLogEntryCreate,
    incident: models.Incident = Depends(dependencies.get_incident_or_404),
    current_user: models.User = Depends(dependencies.get_current_irt_user),
    db: Session = Depends(dependencies.get_db),
):
    """
    Añade una nueva entrada de texto a la bitácora de un incidente existente.

    Requiere que el usuario actual sea un **Miembro IRT**, **Líder IRT** o **Administrador**.
    Esta acción es auditada.

    Args:
        incident_id (int): ID del incidente al que se añade la entrada.
        request (Request): El objeto de la petición HTTP para la auditoría.
        log_in (schemas.ManualLogEntryCreate): El contenido de la entrada de bitácora.
        incident (models.Incident): Dependencia que obtiene el incidente.
        current_user (models.User): Dependencia que valida que el usuario tiene rol de IRT.
        db (Session): Dependencia de la sesión de la base de datos.

    Returns:
        schemas.IncidentLogInDB: La nueva entrada de bitácora creada.
    """
    new_log_entry = incident_service.add_manual_log_entry(
        db, incident=incident, log_in=log_in, user=current_user
    )
    return new_log_entry


@router.post(
    "/{incident_id}/deactivate",
    response_model=schemas.IncidentInDB,
    summary="Desactivar incidente",
)
@audit_action(action="DEACTIVATE_INCIDENT", resource_type="INCIDENT", resource_id_param="incident_id", get_resource_func=crud.incident.get)
def deactivate_incident(
    incident_id: int,
    request: Request,
    incident: models.Incident = Depends(dependencies.get_incident_or_404),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Desactiva un incidente del sistema (soft delete).

    Requiere privilegios de **Administrador**.
    Esta acción es auditada con detalle de cambios.

    Args:
        incident_id (int): ID del incidente a desactivar.
        request (Request): El objeto de la petición HTTP para la auditoría.
        incident (models.Incident): Dependencia que obtiene el incidente o devuelve 404.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): Dependencia que valida rol de Administrador.

    Returns:
        schemas.IncidentInDB: El incidente desactivado.
    """
    deactivated_incident = incident_service.deactivate_incident(db, incident_id=incident.incident_id, performed_by=current_user)
    if deactivated_incident is None:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return deactivated_incident

@router.post(
    "/{incident_id}/activate",
    response_model=schemas.IncidentInDB,
    summary="Activar incidente",
)
@audit_action(action="ACTIVATE_INCIDENT", resource_type="INCIDENT", resource_id_param="incident_id", get_resource_func=crud.incident.get)
def activate_incident(
    incident_id: int,
    request: Request,
    incident: models.Incident = Depends(dependencies.get_incident_or_404),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Activa un incidente previamente desactivado.

    Requiere privilegios de **Administrador**.
    Esta acción es auditada con detalle de cambios.

    Args:
        incident_id (int): ID del incidente a activar.
        request (Request): El objeto de la petición HTTP para la auditoría.
        incident (models.Incident): Dependencia que obtiene el incidente o devuelve 404.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): Dependencia que valida rol de Administrador.

    Returns:
        schemas.IncidentInDB: El incidente activado.
    """
    activated_incident = incident_service.activate_incident(db, incident_id=incident.incident_id)
    if activated_incident is None:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return activated_incident



@router.get(
    "/expertise-areas",
    response_model=Dict[str, Any],
    summary="Obtener áreas de expertise disponibles",
)
def get_expertise_areas(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_irt_user),
):
    """
    Obtiene las áreas de expertise disponibles para asignación de profesionales.

    Returns:
        Dict con áreas de expertise y profesionales disponibles
    """
    try:
        # Obtener usuarios técnicos
        technical_users = db.query(models.User).filter(
            models.User.role.in_([
                models.UserRole.MIEMBRO_IRT,
                models.UserRole.LIDER_IRT,
                models.UserRole.ADMINISTRADOR
            ])
        ).all()

        # Agrupar por áreas de expertise (simplificado)
        expertise_areas = {
            "Redes y Seguridad": [],
            "Protección de Datos": [],
            "Sistemas": [],
            "Usuario Final": [],
            "General": []
        }

        for user in technical_users:
            # Lógica simplificada de asignación de expertise
            # En una implementación real, esto vendría de una tabla de expertise
            if "red" in (user.position or "").lower() or "seguridad" in (user.position or "").lower():
                expertise_areas["Redes y Seguridad"].append({
                    "user_id": user.user_id,
                    "name": user.full_name,
                    "position": user.position,
                })
            elif "datos" in (user.position or "").lower() or "privacidad" in (user.position or "").lower():
                expertise_areas["Protección de Datos"].append({
                    "user_id": user.user_id,
                    "name": user.full_name,
                    "position": user.position,
                })
            elif "sistema" in (user.position or "").lower() or "servidor" in (user.position or "").lower():
                expertise_areas["Sistemas"].append({
                    "user_id": user.user_id,
                    "name": user.full_name,
                    "position": user.position,
                })
            else:
                expertise_areas["General"].append({
                    "user_id": user.user_id,
                    "name": user.full_name,
                    "position": user.position,
                })

        return {
            "success": True,
            "expertise_areas": expertise_areas,
            "total_professionals": len(technical_users)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo áreas de expertise: {str(e)}"
        )


@router.post(
    "/{incident_id}/suggest-assignment",
    response_model=Dict[str, Any],
    summary="Sugerir asignación inteligente de profesional",
)
async def suggest_professional_assignment(
    incident_id: int,
    triage_data: Dict[str, Any] = None,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_irt_user),
):
    """
    Sugiere la asignación de un profesional basado en el análisis del incidente.

    Args:
        incident_id: ID del incidente
        triage_data: Datos del triage (opcional)
        db: Sesión de base de datos
        current_user: Usuario autenticado con rol IRT

    Returns:
        Dict con sugerencia de asignación
    """
    try:
        # Obtener el incidente
        incident = crud.incident.get(db, id=incident_id)
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incidente no encontrado"
            )

        # Verificar permisos
        dependencies.get_incident_with_permission(incident, current_user)

        # Preparar datos de triage
        triage_result = triage_data or {}

        # Obtener sugerencia de asignación
        assignment_suggestion = await incident_triage_service.suggest_professional_assignment(
            db, incident, triage_result
        )

        return {
            "success": True,
            "incident_id": incident_id,
            "assignment_suggestion": assignment_suggestion,
            "message": "Sugerencia de asignación generada exitosamente"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando sugerencia de asignación: {str(e)}"
        )


@router.get(
    "/{incident_id}/evidence/{evidence_file_id}/download",
    response_class=FileResponse,
    summary="Descargar archivo de evidencia",
)
async def download_evidence_file(
    incident_id: int,
    evidence_file_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    Descarga un archivo de evidencia específico de un incidente.

    Valida que el usuario tenga permisos para acceder al incidente y al archivo.
    """
    # Verificar que el incidente existe y el usuario tiene permisos
    incident = dependencies.get_incident_with_permission(incident_id, current_user, db)

    # Obtener el archivo de evidencia
    evidence_file = crud.evidence_file.get(db, id=evidence_file_id)
    if not evidence_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo de evidencia no encontrado"
        )

    # Verificar que el archivo pertenece al incidente
    if evidence_file.incident_id != incident_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El archivo no pertenece a este incidente"
        )

    # Verificar que el archivo existe en el sistema de archivos
    if not os.path.exists(evidence_file.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado en el sistema de archivos"
        )

    # Determinar el tipo de contenido basado en la extensión o tipo MIME almacenado
    content_type = evidence_file.file_type or "application/octet-stream"

    # Devolver el archivo con headers apropiados
    return FileResponse(
        path=evidence_file.file_path,
        media_type=content_type,
        filename=evidence_file.file_name,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{evidence_file.file_name}",
            "Cache-Control": "private, max-age=3600"  # Cache por 1 hora
        }
    )


@router.get(
    "/{incident_id}/evidence",
    response_model=List[schemas.EvidenceFileInDB],
    summary="Obtener lista de archivos de evidencia",
)
def get_incident_evidence_files(
    incident_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    Obtiene la lista de todos los archivos de evidencia para un incidente específico.

    Valida que el usuario tenga permisos para acceder al incidente.
    """
    # Verificar que el incidente existe y el usuario tiene permisos
    dependencies.get_incident_with_permission(incident_id, current_user, db)

    # Obtener todos los archivos de evidencia del incidente
    evidence_files = crud.evidence_file.get_by_incident(db, incident_id=incident_id)

    return evidence_files

@router.get("/{incident_id}/report", response_class=HTMLResponse)
async def get_incident_report(
    incident_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    Genera y devuelve un informe de incidente en formato HTML.
    """
    incident = crud.incident.get(db, id=incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidente no encontrado.")

    # TODO: Add authorization logic here

    html_content = report_service.generate_incident_report_html(incident)

    return HTMLResponse(content=html_content)