"""
Servicio de Triage Inteligente para Incidentes ISIRT.

Este servicio orquesta los diferentes servicios especializados para el manejo
completo del ciclo de vida de un incidente de seguridad.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from incident_api import models
from incident_api.services.initial_triage_service import initial_triage_service
from incident_api.services.assignment_suggestion_service import assignment_suggestion_service
from incident_api.services.isirt_analysis_service import isirt_analysis_service
from incident_api.services.closure_report_service import closure_report_service
import logging

logger = logging.getLogger(__name__)


class IncidentTriageService:
    """
    Servicio principal de triage que orquesta los servicios especializados.
    """

    async def perform_initial_triage(
        self, db: Session, incident: models.Incident
    ) -> Dict[str, Any]:
        """
        Realiza el triage inicial del incidente delegando al servicio especializado.

        Args:
            db: Sesión de base de datos
            incident: El incidente a analizar

        Returns:
            Dict con recomendaciones de triage
        """
        return await initial_triage_service.perform_initial_triage(db, incident)

    async def generate_isirt_analysis(
        self, db: Session, incident: models.Incident, additional_context: str = ""
    ) -> Dict[str, Any]:
        """
        Genera un análisis detallado para el equipo ISIRT delegando al servicio especializado.

        Args:
            db: Sesión de base de datos
            incident: El incidente a analizar
            additional_context: Contexto adicional proporcionado por el analista

        Returns:
            Dict con análisis detallado para ISIRT
        """
        return await isirt_analysis_service.generate_isirt_analysis(db, incident, additional_context)

    async def generate_closure_report(
        self, db: Session, incident: models.Incident
    ) -> Dict[str, Any]:
        """
        Genera el reporte final de cierre del incidente delegando al servicio especializado.

        Args:
            db: Sesión de base de datos
            incident: El incidente cerrado

        Returns:
            Dict con el reporte completo del incidente
        """
        return await closure_report_service.generate_closure_report(db, incident)

    async def suggest_professional_assignment(
        self, db: Session, incident: models.Incident, triage_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sugiere la asignación de un profesional delegando al servicio especializado.

        Args:
            db: Sesión de base de datos
            incident: El incidente a asignar
            triage_result: Resultados del triage

        Returns:
            Dict con sugerencia de asignación
        """
        return await assignment_suggestion_service.suggest_professional_assignment(
            db, incident, triage_result
        )


# Instancia global del servicio
incident_triage_service = IncidentTriageService()