"""
Servicio de Triage Inicial para Incidentes ISIRT.

Este servicio se encarga del triage inicial de incidentes,
clasificación automática y evaluación preliminar.
"""

import json
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from incident_api import models, schemas
from incident_api.services.ai_settings_service import get_active_settings
from incident_api.services.incident_analysis_service import incident_analysis_service
from incident_api.services.assignment_suggestion_service import assignment_suggestion_service
import logging

logger = logging.getLogger(__name__)


class InitialTriageService:
    """
    Servicio para el triage inicial de incidentes.
    """

    async def perform_initial_triage(
        self, db: Session, incident: models.Incident
    ) -> Dict[str, Any]:
        """
        Realiza el triage inicial del incidente usando IA.

        Args:
            db: Sesión de base de datos
            incident: El incidente a analizar

        Returns:
            Dict con recomendaciones de triage
        """
        try:
            ai_settings = get_active_settings(db)
            if not ai_settings:
                logger.warning("No AI settings available for triage")
                return self._get_fallback_triage()

            # Preparar contexto del incidente
            incident_context = self._prepare_incident_context(incident)

            # Realizar análisis con IA
            triage_result = await self._analyze_with_ai(incident_context, ai_settings)

            # Procesar y validar resultados
            processed_result = self._process_triage_result(triage_result)

            # Sugerir profesional asignado
            professional_suggestion = await assignment_suggestion_service.suggest_professional_assignment(
                db, incident, processed_result
            )

            processed_result["suggested_assignee"] = professional_suggestion

            logger.info(f"Triage completed for incident {incident.incident_id}")
            return processed_result

        except Exception as e:
            logger.error(f"Error in initial triage for incident {incident.incident_id}: {e}")
            return self._get_fallback_triage()

    def _prepare_incident_context(self, incident: models.Incident) -> Dict[str, Any]:
        """Prepara el contexto del incidente para el análisis de IA."""
        return {
            "ticket_id": incident.ticket_id,
            "summary": incident.summary,
            "description": incident.description,
            "discovery_time": incident.discovery_time.isoformat() if incident.discovery_time else None,
            "reported_by": incident.reporter.full_name if incident.reporter else "Unknown",
            "asset_info": {
                "asset_name": incident.asset.name if incident.asset else None,
                "asset_type": incident.asset.asset_type.name if incident.asset and incident.asset.asset_type else None,
            } if incident.asset else None,
            "current_status": incident.status,
            "ai_conversation": incident.ai_conversation,
        }

    async def _analyze_with_ai(
        self, incident_context: Dict[str, Any], ai_settings: Any
    ) -> Dict[str, Any]:
        """Realiza el análisis del incidente usando IA."""
        try:
            # Usar el servicio de análisis de incidentes existente
            analysis_result = await incident_analysis_service.get_incident_analysis(
                db=None,  # No necesitamos db aquí
                incident_data=incident_context,
                settings=ai_settings
            )

            return analysis_result if analysis_result else {}

        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return {}

    def _process_triage_result(self, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa y valida los resultados del análisis de IA."""
        processed = {
            "classification": {
                "category": ai_result.get("suggested_category", "Sin clasificar"),
                "incident_type": ai_result.get("suggested_type", "Sin especificar"),
                "attack_vector": ai_result.get("attack_vector", "Sin determinar"),
            },
            "severity": {
                "suggested_level": ai_result.get("severity", "SEV-3 (Medio)"),
                "justification": ai_result.get("severity_justification", "Evaluación preliminar"),
            },
            "impact_assessment": {
                "confidentiality": ai_result.get("impact_confidentiality", 0),
                "integrity": ai_result.get("impact_integrity", 0),
                "availability": ai_result.get("impact_availability", 0),
                "total_impact": ai_result.get("total_impact", 0),
            },
            "immediate_actions": ai_result.get("immediate_actions", []),
            "preliminary_analysis": ai_result.get("preliminary_analysis", ""),
            "risk_assessment": ai_result.get("risk_assessment", ""),
        }

        return processed

    def _get_fallback_triage(self) -> Dict[str, Any]:
        """Proporciona un triage básico cuando la IA no está disponible."""
        return {
            "classification": {
                "category": "Sin clasificar",
                "incident_type": "Requiere revisión manual",
                "attack_vector": "Sin determinar",
            },
            "severity": {
                "suggested_level": "SEV-3 (Medio)",
                "justification": "Evaluación manual requerida",
            },
            "impact_assessment": {
                "confidentiality": 0,
                "integrity": 0,
                "availability": 0,
                "total_impact": 0,
            },
            "immediate_actions": [
                "Revisar logs del sistema",
                "Aislar sistemas afectados",
                "Documentar hallazgos",
            ],
            "preliminary_analysis": "Requiere análisis manual por equipo ISIRT",
            "risk_assessment": "Evaluación pendiente",
            "suggested_assignee": {
                "suggested_user": None,
                "reason": "Asignación manual requerida",
            },
        }


# Instancia global del servicio
initial_triage_service = InitialTriageService()