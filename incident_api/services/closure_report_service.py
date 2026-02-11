"""
Servicio de Reportes de Cierre para Incidentes ISIRT.

Este servicio genera reportes finales de cierre de incidentes
para almacenamiento en el sistema RAG.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from incident_api import models
import logging

logger = logging.getLogger(__name__)


class ClosureReportService:
    """
    Servicio para generar reportes de cierre de incidentes.
    """

    async def generate_closure_report(
        self, db: Session, incident: models.Incident
    ) -> Dict[str, Any]:
        """
        Genera el reporte final de cierre del incidente para RAG.

        Args:
            db: Sesión de base de datos
            incident: El incidente cerrado

        Returns:
            Dict con el reporte completo del incidente
        """
        try:
            report = {
                "incident_summary": {
                    "ticket_id": incident.ticket_id,
                    "summary": incident.summary,
                    "description": incident.description,
                    "status": incident.status,
                    "severity": incident.severity,
                    "created_at": incident.created_at.isoformat() if incident.created_at else None,
                    "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
                },
                "classification": {
                    "category": incident.incident_category.name if incident.incident_category else None,
                    "type": incident.incident_type.name if incident.incident_type else None,
                    "attack_vector": incident.attack_vector.name if incident.attack_vector else None,
                },
                "assignment": {
                    "reported_by": incident.reporter.full_name if incident.reporter else None,
                    "assigned_to": incident.assignee.full_name if incident.assignee else None,
                    "assigned_group": incident.assignee_group.name if incident.assignee_group else None,
                },
                "impact_assessment": {
                    "confidentiality": incident.impact_confidentiality,
                    "integrity": incident.impact_integrity,
                    "availability": incident.impact_availability,
                    "total_impact": incident.total_impact,
                },
                "analysis_response": {
                    "root_cause": incident.root_cause_analysis,
                    "corrective_actions": incident.corrective_actions,
                    "lessons_learned": incident.lessons_learned,
                    "recommendations": incident.recommendations,
                },
                "evidence": [
                    {
                        "filename": evidence.file_name,
                        "type": evidence.file_type,
                        "size": evidence.file_size_bytes,
                        "uploaded_at": evidence.uploaded_at.isoformat() if evidence.uploaded_at else None,
                    }
                    for evidence in incident.evidence_files
                ] if incident.evidence_files else [],
                "timeline": [
                    {
                        "timestamp": log_entry.timestamp.isoformat() if log_entry.timestamp else None,
                        "action": log_entry.action,
                        "user": log_entry.user.full_name if log_entry.user else None,
                        "comments": log_entry.comments,
                    }
                    for log_entry in incident.logs
                ] if incident.logs else [],
            }

            return report

        except Exception as e:
            logger.error(f"Error generating closure report: {e}")
            return {"error": f"Error generando reporte de cierre: {str(e)}"}


# Instancia global del servicio
closure_report_service = ClosureReportService()