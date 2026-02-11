"""
Unit tests for the Incident Analysis Service.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from sqlalchemy.orm import Session
from langchain_core.documents import Document

from incident_api.services.incident_analysis_service import incident_analysis_service
from incident_api.models import Incident, AIModelSettings, IncidentCategory, IncidentSeverity
from incident_api.schemas import IncidentEnrichmentResponse, TriageAnalysis, ResponseRecommendations

@pytest.mark.asyncio
@patch("incident_api.services.incident_analysis_service.llm_service")
@patch("incident_api.services.incident_analysis_service.rag_retrieval_service")
async def test_get_incident_enrichment_calculates_confidence_and_traceability(
    mock_rag_retrieval: MagicMock,
    mock_llm_service: MagicMock,
    db_session_override: Session, # Fixture
):
    """
    Test that get_incident_enrichment correctly processes the RAG context,
    calculates confidence, and returns a structured response.
    """
    # --- Arrange ---

    # 1. Mock the response from the RAG retrieval service
    retrieved_items = [
        {"doc": Document(page_content="Doc 1", metadata={"source_name": "s1.md", "source_version": "v1"}), "score": 0.78},
        {"doc": Document(page_content="Doc 2", metadata={"source_name": "s2.md", "source_version": "v2"}), "score": 0.65},
    ]
    mock_rag_retrieval.retrieve_context = AsyncMock(return_value=retrieved_items)

    # 2. Mock the response from the LLM service
    mock_enrichment = IncidentEnrichmentResponse(
        executive_summary="This is a test summary.",
        triage_analysis=TriageAnalysis(potential_attack_vector="test", affected_assets_assessment="test", initial_severity_assessment="SEV-3 (Medio)"),
        response_recommendations=ResponseRecommendations(containment_steps=["step1"], eradication_steps=[], recovery_steps=[]),
        communication_guidelines="test guidelines"
    )
    mock_llm_service.invoke_for_json = AsyncMock(return_value=mock_enrichment.dict())
    # 3. Create mock input objects
    mock_incident = Incident(
        incident_id=1,
        summary="Test Incident",
        description="Test description",
        incident_category=IncidentCategory(name="Test Category"),
        severity=IncidentSeverity.SEV3
    )
    mock_settings = AIModelSettings()

    # --- Act ---
    result = await incident_analysis_service.get_incident_enrichment(
        db=db_session_override, incident=mock_incident, settings=mock_settings
    )

    # --- Assert ---
    assert "enrichment" in result
    assert "rag_suggestion" in result

    # Assert confidence level calculation (0.78 + 0.65) / 2 = 0.715, which is 'Media'
    assert result["rag_suggestion"]["confidence_level"] == "Media"

    # Assert source traceability
    sources = result["rag_suggestion"]["sources"]
    assert len(sources) == 2
    assert sources[0]["source_name"] == "s1.md"
    assert sources[0]["confidence_score"] == 0.78
    assert sources[1]["source_name"] == "s2.md"
    assert sources[1]["confidence_score"] == 0.65

    # Assert that the enrichment data is passed through correctly
    assert result["enrichment"]["executive_summary"] == "This is a test summary."
