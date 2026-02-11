"""
CRUD operations for the KnowledgeCuration model.
"""
from typing import Optional
from sqlalchemy.orm import Session

from incident_api.crud.base import CRUDBase
from incident_api.models.knowledge_curation import KnowledgeCuration
from incident_api.schemas.knowledge_curation import KnowledgeCurationCreate, KnowledgeCurationUpdate

class CRUDKnowledgeCuration(CRUDBase[KnowledgeCuration, KnowledgeCurationCreate, KnowledgeCurationUpdate]):
    def get_by_source_and_chunk(
        self, db: Session, *, source_name: str, chunk_id: str
    ) -> Optional[KnowledgeCuration]:
        """
        Get a curation record by its source name and chunk ID.
        """
        return (
            db.query(self.model)
            .filter(self.model.source_name == source_name, self.model.chunk_id == chunk_id)
            .first()
        )

knowledge_curation = CRUDKnowledgeCuration(KnowledgeCuration)
