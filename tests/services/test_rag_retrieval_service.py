"""
Unit tests for the RAG Retrieval Service.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from sqlalchemy.orm import Session
from langchain_core.documents import Document

from incident_api.services.rag_retrieval_service import rag_retrieval_service
from incident_api.models.knowledge_curation import KnowledgeCuration

@pytest.mark.asyncio
@patch("incident_api.services.rag_retrieval_service.crud.knowledge_curation")
@patch("incident_api.services.rag_retrieval_service.RAGProcessor")
async def test_retrieve_context_filters_flagged_chunks(
    mock_rag_processor: MagicMock,
    mock_crud_curation: MagicMock,
    db_session_override: Session, # Fixture from conftest.py
):
    """
    Test that retrieve_context correctly filters out documents that are flagged
    in the knowledge_curation table.
    """
    # --- Arrange ---
    
    # 1. Mock RAGProcessor and its retriever
    mock_retriever = AsyncMock()
    mock_rag_processor.return_value.get_retriever.return_value = mock_retriever

    # 2. Define the documents that the mock retriever will return
    doc1 = Document(page_content="Contenido del Playbook de Phishing.", metadata={"source_name": "playbook_phishing.md", "chunk_id": "chunk_0", "score": 0.9})
    doc2 = Document(page_content="Contenido obsoleto.", metadata={"source_name": "playbook_obsoleto.md", "chunk_id": "chunk_1", "score": 0.8})
    doc3 = Document(page_content="Contenido de MITRE sobre T1566.", metadata={"source_name": "mitre_T1566.json", "chunk_id": "chunk_2", "score": 0.85})
    
    mock_retriever.ainvoke.return_value = [doc1, doc2, doc3]

    # 3. Mock the CRUD operation for knowledge curation
    def mock_get_by_source_and_chunk(db, source_name, chunk_id):
        if source_name == "playbook_obsoleto.md" and chunk_id == "chunk_1":
            return KnowledgeCuration(status="flagged")
        return None

    mock_crud_curation.get_by_source_and_chunk.side_effect = mock_get_by_source_and_chunk

    # --- Act ---
    prompt = "cómo manejar un ataque de phishing"
    retrieved_items = await rag_retrieval_service.retrieve_context(db_session_override, prompt)

    # --- Assert ---
    
    # Check that the result contains 2 items (doc1 and doc3)
    assert len(retrieved_items) == 2

    # Check that the flagged document (doc2) is not in the results
    retrieved_contents = [item["doc"].page_content for item in retrieved_items]
    assert "Contenido obsoleto." not in retrieved_contents
    assert "Contenido del Playbook de Phishing." in retrieved_contents

    # Check that the scores are preserved
    assert retrieved_items[0]["score"] == 0.9
    assert retrieved_items[1]["score"] == 0.85

    # Verify that the mock CRUD was called for each document
    assert mock_crud_curation.get_by_source_and_chunk.call_count == 3
