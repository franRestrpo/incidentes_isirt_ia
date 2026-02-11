"""
Servicio para la recuperación de contexto usando RAG.
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from incident_api import crud
from incident_api.ai.rag_processor import RAGProcessor

logger = logging.getLogger(__name__)

class RAGRetrievalService:
    """
    Servicio para recuperar contexto de documentos usando RAG.
    """

    async def retrieve_context(self, db: Session, prompt: str) -> List[Dict[str, Any]]:
        """
        Obtiene contexto de los playbooks usando RAG, incluyendo puntuaciones y 
        filtrando por el estado de curación.
        """
        try:
            rag_processor = RAGProcessor()
            # Usamos un umbral de score bajo para recuperar más docs y luego filtrar
            retriever = rag_processor.get_retriever(score_threshold=0.5)
            
            # Langchain ha cambiado el método, usamos el genérico invoke
            docs_with_scores = await retriever.ainvoke(prompt)

            # Langchain ahora devuelve Documentos con scores en su metadata
            # por lo que procesamos para unificar el formato.
            processed_docs = []
            for doc in docs_with_scores:
                score = doc.metadata.get('score', 0)
                processed_docs.append({"doc": doc, "score": score})

            # Filtrar documentos según el estado de curación
            curated_docs = []
            for item in processed_docs:
                doc = item["doc"]
                source_name = doc.metadata.get("source_name")
                chunk_id = doc.metadata.get("chunk_id")

                if source_name and chunk_id:
                    curation_status = crud.knowledge_curation.get_by_source_and_chunk(
                        db, source_name=source_name, chunk_id=chunk_id
                    )
                    if curation_status and curation_status.status != "active":
                        logger.info(f"Excluyendo chunk {chunk_id} de {source_name} por estado de curación: {curation_status.status}")
                        continue  # No incluir este chunk
                
                curated_docs.append(item)

            return curated_docs

        except FileNotFoundError:
            logger.warning("Índice FAISS no encontrado. El chatbot responderá sin contexto de playbooks.")
        except Exception:
            logger.error("Error no esperado al obtener el contexto RAG. El chatbot responderá sin contexto.", exc_info=True)
        
        return []

rag_retrieval_service = RAGRetrievalService()