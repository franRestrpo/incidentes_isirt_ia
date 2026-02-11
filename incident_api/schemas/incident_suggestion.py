"""
Esquemas de Pydantic para las sugerencias de IA para incidentes.
"""

from typing import Optional
from pydantic import BaseModel, Field
from incident_api.models.incident import IncidentSeverity

class IncidentSuggestionRequest(BaseModel):
    """Esquema para solicitar sugerencias de incidentes desde la IA."""
    description: str = Field(..., min_length=20, description="Descripción detallada del incidente proporcionada por el usuario.")

class IncidentSuggestionResponse(BaseModel):
    """Esquema para las sugerencias de la IA para un reporte de incidente."""
    suggested_title: str
    suggested_category_id: int
    suggested_severity: IncidentSeverity
    suggested_incident_type_id: Optional[int] = None
    suggested_user_id: Optional[int] = None
