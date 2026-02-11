"""
Esquemas de Pydantic para el resumen de diálogos de incidentes por IA.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class DialogueSummaryRequest(BaseModel):
    """Esquema para solicitar un resumen del diálogo de un incidente."""
    conversation_history: List[Dict[str, Any]] = Field(..., description="El historial completo de conversación entre el usuario y el asistente de IA.")

class DialogueSummaryResponse(BaseModel):
    """Esquema para el resumen generado por la IA del diálogo."""
    summary: str = Field(..., description="El resumen conciso/título para el incidente.")
    detailed_description: str = Field(..., description="La descripción detallada y estructurada del incidente generada a partir del diálogo.")
