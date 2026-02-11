"""
Servicio de Análisis ISIRT para Incidentes.

Este servicio genera análisis detallados para el equipo ISIRT
durante la respuesta a incidentes.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from incident_api import models
from incident_api.services.ai_settings_service import get_active_settings
from incident_api.services.llm_service import llm_service
from incident_api.services.ai_text_utils import sanitize_for_prompt
from langchain_core.messages import SystemMessage, HumanMessage
import logging

logger = logging.getLogger(__name__)


class ISIRTAnalysisService:
    """
    Servicio para generar análisis detallados para el equipo ISIRT.
    """

    async def generate_isirt_analysis(
        self, db: Session, incident: models.Incident, additional_context: str = ""
    ) -> Dict[str, Any]:
        """
        Genera un análisis detallado para el equipo ISIRT.

        Args:
            db: Sesión de base de datos
            incident: El incidente a analizar
            additional_context: Contexto adicional proporcionado por el analista

        Returns:
            Dict con análisis detallado para ISIRT
        """
        try:
            ai_settings = get_active_settings(db)
            if not ai_settings:
                return {"error": "Configuración de IA no disponible"}

            # Preparar contexto completo del incidente
            full_context = {
                "incident_data": self._prepare_incident_context(incident),
                "current_status": incident.status,
                "assigned_user": incident.assignee.full_name if incident.assignee else None,
                "additional_context": additional_context,
                "evidence_count": len(incident.evidence_files) if incident.evidence_files else 0,
                "logs_count": len(incident.logs) if incident.logs else 0,
            }

            # Generar análisis ISIRT
            isirt_analysis = await self._generate_isirt_analysis_with_ai(full_context, ai_settings)

            return {
                "root_cause_analysis": isirt_analysis.get("root_cause", ""),
                "containment_actions": isirt_analysis.get("containment", []),
                "recovery_actions": isirt_analysis.get("recovery", []),
                "lessons_learned": isirt_analysis.get("lessons_learned", []),
                "corrective_actions": isirt_analysis.get("corrective_actions", []),
                "preventive_measures": isirt_analysis.get("preventive_measures", []),
                "iso27001_compliance": isirt_analysis.get("compliance_notes", ""),
            }

        except Exception as e:
            logger.error(f"Error generating ISIRT analysis: {e}")
            return {"error": f"Error en análisis ISIRT: {str(e)}"}

    def _prepare_incident_context(self, incident: models.Incident) -> Dict[str, Any]:
        """Prepara el contexto del incidente para el análisis ISIRT."""
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

    async def _generate_isirt_analysis_with_ai(
        self, context: Dict[str, Any], ai_settings: Any
    ) -> Dict[str, Any]:
        """
        Genera análisis ISIRT usando IA.

        Delega la invocación de LLM al servicio correspondiente.
        """
        try:
            incident_data = context.get("incident_data", {})
            additional_context = context.get("additional_context", "")

            system_prompt = f"""
            Eres un analista senior de respuesta a incidentes (ISIRT) especializado en ciberseguridad según ISO 27001:2022.

            Tu tarea es analizar un incidente de seguridad y proporcionar un análisis detallado para el equipo de respuesta.

            Información del incidente:
            - Ticket: {sanitize_for_prompt(incident_data.get('ticket_id', 'N/A'))}
            - Título: {sanitize_for_prompt(incident_data.get('summary', 'N/A'))}
            - Descripción: {sanitize_for_prompt(incident_data.get('description', 'N/A'))}
            - Estado actual: {sanitize_for_prompt(str(incident_data.get('current_status', 'N/A')))}
            - Usuario asignado: {sanitize_for_prompt(context.get('assigned_user', 'No asignado'))}
            - Evidencia disponible: {context.get('evidence_count', 0)} archivos
            - Entradas en bitácora: {context.get('logs_count', 0)}

            Contexto adicional proporcionado por el analista: {sanitize_for_prompt(additional_context) if additional_context else "Ninguno"}

            Debes devolver SÓLO un objeto JSON válido con el siguiente análisis detallado:

            {{
              "root_cause": "Análisis detallado de la causa raíz del incidente. Identifica vulnerabilidades, fallos de configuración, errores humanos, etc.",
              "containment": [
                "Acción inmediata 1 para contener el incidente",
                "Acción inmediata 2 para contener el incidente",
                "Acción inmediata 3 para contener el incidente"
              ],
              "recovery": [
                "Paso 1 para restaurar sistemas/servicios",
                "Paso 2 para restaurar sistemas/servicios",
                "Paso 3 para restaurar sistemas/servicios"
              ],
              "lessons_learned": [
                "¿Qué funcionó bien en la respuesta?",
                "¿Qué se puede mejorar en procesos?",
                "¿Qué capacitación adicional se necesita?"
              ],
              "corrective_actions": [
                "Acción correctiva específica 1 (con responsable y fecha límite)",
                "Acción correctiva específica 2 (con responsable y fecha límite)",
                "Acción correctiva específica 3 (con responsable y fecha límite)"
              ],
              "preventive_measures": [
                "Medida preventiva 1 para evitar recurrencia",
                "Medida preventiva 2 para evitar recurrencia",
                "Medida preventiva 3 para evitar recurrencia"
              ],
              "compliance_notes": "Notas sobre cumplimiento ISO 27001:2022, controles afectados y recomendaciones de mejora"
            }}

            El análisis debe ser específico, accionable y basado en las mejores prácticas de respuesta a incidentes.
            """

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content="Genera el análisis ISIRT completo para este incidente.")
            ]

            analysis_result = await llm_service.invoke_for_json(messages, ai_settings)
            logger.info("Análisis ISIRT generado exitosamente por IA")

            return analysis_result

        except Exception as e:
            logger.error(f"Error in ISIRT AI analysis: {e}")
            # Return fallback analysis if AI fails
            return {
                "root_cause": f"Error en análisis automático: {str(e)}. Requiere revisión manual.",
                "containment": ["Revisar manualmente acciones de contención"],
                "recovery": ["Evaluar manualmente pasos de recuperación"],
                "lessons_learned": ["Documentar lecciones aprendidas manualmente"],
                "corrective_actions": ["Definir acciones correctivas manualmente"],
                "preventive_measures": ["Implementar medidas preventivas basadas en revisión manual"],
                "compliance_notes": "Revisar cumplimiento ISO 27001 manualmente",
            }


# Instancia global del servicio
isirt_analysis_service = ISIRTAnalysisService()