"""
Esquemas para respuestas de análisis de IA.
"""

from pydantic import BaseModel
from typing import List, Optional


class TriageAnalysis(BaseModel):
    potential_attack_vector: str
    affected_assets_assessment: str
    initial_severity_assessment: str


class ResponseRecommendations(BaseModel):
    containment_steps: List[str]
    eradication_steps: List[str]
    recovery_steps: List[str]


class IncidentEnrichmentResponse(BaseModel):
    executive_summary: str
    triage_analysis: TriageAnalysis
    response_recommendations: ResponseRecommendations
    communication_guidelines: str


class ISIRTAnalysisRequest(BaseModel):
    additional_context: str = ""

# --- Schemas for RAG Suggestions with Traceability ---

class SourceFragment(BaseModel):
    """Schema for a single piece of retrieved knowledge."""
    source_name: str
    source_version: Optional[str] = None
    content: str
    confidence_score: float

class RAGSuggestion(BaseModel):
    """Schema for the complete RAG suggestion response."""
    suggestion_text: str
    confidence_level: str
    sources: List[SourceFragment]