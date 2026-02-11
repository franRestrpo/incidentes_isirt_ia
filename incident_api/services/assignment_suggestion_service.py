"""
Servicio de Sugerencia de Asignación para Incidentes ISIRT.

Este servicio se encarga de sugerir profesionales para asignar
a incidentes basándose en expertise y disponibilidad.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session

from incident_api import models
from incident_api.models import UserRole
import logging

logger = logging.getLogger(__name__)


class AssignmentSuggestionService:
    """
    Servicio para sugerir asignación de profesionales a incidentes.
    """

    async def suggest_professional_assignment(
        self, db: Session, incident: models.Incident, triage_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sugiere la asignación de un profesional basado en el análisis del triage.

        Args:
            db: Sesión de base de datos
            incident: El incidente a asignar
            triage_result: Resultados del triage

        Returns:
            Dict con sugerencia de asignación
        """
        try:
            # Obtener usuarios con roles técnicos
            technical_users = db.query(models.User).filter(
                models.User.role.in_([
                    UserRole.MIEMBRO_IRT,
                    UserRole.LIDER_IRT,
                    UserRole.ADMINISTRADOR
                ])
            ).all()

            if not technical_users:
                return {"suggested_user": None, "reason": "No hay profesionales técnicos disponibles"}

            # Lógica simple de asignación basada en categoría
            category = triage_result.get("classification", {}).get("category", "").lower()

            # Asignar basado en especialización
            if "red" in category or "seguridad" in category:
                expertise_area = "Redes y Seguridad"
            elif "datos" in category or "privacidad" in category:
                expertise_area = "Protección de Datos"
            elif "sistema" in category or "servidor" in category:
                expertise_area = "Sistemas"
            else:
                expertise_area = "General"

            # Por ahora, asignar al primer usuario disponible
            # En una implementación real, se podría tener una base de datos de expertise
            suggested_user = technical_users[0] if technical_users else None

            return {
                "suggested_user": suggested_user.user_id if suggested_user else None,
                "suggested_user_name": suggested_user.full_name if suggested_user else None,
                "expertise_area": expertise_area,
                "reason": f"Asignación basada en especialización en {expertise_area}",
            }

        except Exception as e:
            logger.error(f"Error suggesting professional assignment: {e}")
            return {"suggested_user": None, "reason": "Error en asignación automática"}


# Instancia global del servicio
assignment_suggestion_service = AssignmentSuggestionService()