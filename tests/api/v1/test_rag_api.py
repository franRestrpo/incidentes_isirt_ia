"""
Integration tests for the RAG Curation API endpoint.
"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from incident_api import crud
from incident_api.core.config import settings


def test_flag_knowledge_chunk_as_admin(
    test_client: TestClient, 
    admin_user_token_headers: dict, 
    db_session_override: Session
):
    """
    Test that an admin user can successfully flag a knowledge chunk.
    """
    # --- Arrange ---
    curation_payload = {
        "source_name": "test_playbook.md",
        "chunk_id": "test_chunk_123",
        "notes": "This information is outdated."
    }

    # --- Act ---
    response = test_client.post(
        f"{settings.API_V1_STR}/rag/curate",
        headers=admin_user_token_headers,
        json=curation_payload,
    )

    # --- Assert ---
    assert response.status_code == 200
    assert response.json()["message"] == "Knowledge chunk flagged successfully. It will be excluded from future suggestions pending review."

    # Verify the record in the database
    db_record = crud.knowledge_curation.get_by_source_and_chunk(
        db_session_override, 
        source_name="test_playbook.md", 
        chunk_id="test_chunk_123"
    )
    
    assert db_record is not None
    assert db_record.status == "flagged"
    assert db_record.notes.endswith("This information is outdated.")
    assert db_record.flagged_by_user_id is not None
