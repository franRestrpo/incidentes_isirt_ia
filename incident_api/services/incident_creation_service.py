"""
Servicio para la lógica de negocio relacionada con la creación de incidentes.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from datetime import datetime, timezone
from pydantic import ValidationError
import logging

from incident_api import crud, models, schemas
from incident_api.schemas import IncidentCreateFromString
from incident_api.services.incident_analysis_service import incident_analysis_service
from incident_api.services.ai_settings_service import get_active_settings
from incident_api.services.file_storage_service import file_storage_service
from incident_api.services.log_service import log_service
from incident_api.services.history_service import history_service

logger = logging.getLogger(__name__)


class IncidentCreationService:
    """
    Clase de servicio para gestionar la lógica de negocio de la creación de incidentes.
    """

    async def create_incident_from_json_string(
        self,
        db: Session,
        *,
        incident_data_str: str,
        user: models.User,
        evidence_files: Optional[List[UploadFile]] = None,
    ) -> models.Incident:
        """
        Crea un incidente a partir de un string JSON, validándolo primero.
        """
        try:
            incident_in = IncidentCreateFromString.validate_json(incident_data_str)
        except ValidationError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El JSON proporcionado es inválido o le faltan campos.",
            )
        
        return await self.create_incident(
            db, incident_in=incident_in, user=user, evidence_files=evidence_files
        )

    async def create_incident(
        self,
        db: Session,
        *,
        incident_in: schemas.IncidentCreate,
        user: models.User,
        evidence_files: Optional[List[UploadFile]] = None,
    ) -> models.Incident:
        """
        Crea un nuevo incidente coordinando las operaciones necesarias.
        """
        logger.info(f"Iniciando creación de incidente - Usuario: {user.user_id}, Título: {incident_in.summary[:50]}...")
        start_time = datetime.now(timezone.utc)

        try:
            # Crear el incidente en la base de datos
            new_incident = self._create_incident_record(db, incident_in, user)
            logger.info(f"Incidente creado en BD - ID: {new_incident.incident_id}, Ticket: {new_incident.ticket_id}")

            # Manejar la carga de archivos de evidencia
            if evidence_files:
                logger.info(f"Procesando {len(evidence_files)} archivo(s) de evidencia")
                self._handle_evidence_upload(
                    db, incident=new_incident, files=evidence_files, uploader=user
                )
                logger.info("Archivos de evidencia procesados exitosamente")
            else:
                logger.debug("No se proporcionaron archivos de evidencia")

            # Registrar la creación en la bitácora y el historial
            self._log_incident_creation(db, new_incident, user)
            logger.debug("Entrada de bitácora y historial creados para el incidente")

            # Enriquecer el incidente con IA
            await self._enrich_incident_with_ai(db, new_incident)

            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"Incidente creado exitosamente - ID: {new_incident.incident_id}, Duración: {duration:.2f}s")

            return new_incident

        except Exception as e:
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(f"Error al crear incidente - Usuario: {user.user_id}, Duración: {duration:.2f}s, Error: {str(e)}", exc_info=True)
            # Aquí se podría añadir lógica para rollback de archivos si fuera necesario
            raise

    def _create_incident_record(
        self, db: Session, incident_in: schemas.IncidentCreate, user: models.User
    ) -> models.Incident:
        """
        Crea el registro del incidente en la base de datos.
        """
        return crud.incident.create(
            db, obj_in=incident_in, reported_by_id=user.user_id
        )

    def _log_incident_creation(
        self, db: Session, incident: models.Incident, user: models.User
    ):
        """
        Registra la creación del incidente en la bitácora y el historial.
        """
        log_service.create_incident_log(
            db, incident.incident_id, user.user_id,
            "Creación", "Incidente reportado inicialmente."
        )
        history_service.create_incident_history(
            db,
            incident_id=incident.incident_id,
            user_id=user.user_id,
            obj_in=schemas.IncidentHistoryCreate(
                field_changed="Creación",
                old_value=None,
                new_value="Incidente creado",
                details=f"Incidente {incident.ticket_id} reportado por {user.email}"
            )
        )

    async def _enrich_incident_with_ai(self, db: Session, incident: models.Incident):
        """
        Enriquecer el incidente con datos de IA.
        """
        try:
            ai_settings = get_active_settings(db)
            enrichment_data = await incident_analysis_service.get_incident_enrichment(
                db, incident=incident, settings=ai_settings
            )
            if enrichment_data:
                crud.incident.update(db, db_obj=incident, obj_in={"ai_recommendations": enrichment_data})
                logger.info(f"Incidente {incident.incident_id} enriquecido exitosamente por la IA.")
        except Exception as e:
            logger.error(f"Fallo en el enriquecimiento por IA para el incidente {incident.incident_id}: {e}")

    def _handle_evidence_upload(
        self,
        db: Session,
        incident: models.Incident,
        files: List[UploadFile],
        uploader: models.User,
    ):
        """Maneja de forma segura la validación y guardado de archivos de evidencia."""
        logger.debug(f"Iniciando procesamiento de {len(files)} archivo(s) para incidente {incident.incident_id}")

        saved_files = file_storage_service.save_evidence_files(incident.incident_id, files)

        for file_info in saved_files:
            evidence_in = schemas.EvidenceFileCreate(
                file_name=file_info['file_name'],
                file_type=file_info['file_type'],
                file_size_bytes=file_info['file_size'],
                file_hash=file_info['file_hash'],
            )
            crud.evidence_file.create_with_incident_and_uploader(
                db,
                obj_in=evidence_in,
                incident_id=incident.incident_id,
                uploader_id=uploader.user_id,
                file_path=file_info['file_path'],
            )
            logger.debug(f"Registro de evidencia creado en BD para archivo: {file_info['file_name']}")


incident_creation_service = IncidentCreationService()
