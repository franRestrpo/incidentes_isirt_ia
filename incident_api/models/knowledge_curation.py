"""
SQLAlchemy model for the Knowledge Curation feature.

This model defines the `knowledge_curation` table, which stores the status and
feedback for each piece of knowledge (chunk) used by the RAG system.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from incident_api.db.base import Base

class KnowledgeCuration(Base):
    __tablename__ = "knowledge_curation"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiers for the knowledge chunk
    source_name = Column(String, nullable=False, index=True)
    chunk_id = Column(String, nullable=False, index=True)

    # Curation status
    status = Column(String, nullable=False, default="active", index=True)  # e.g., active, flagged, obsolete

    # User feedback details
    flagged_by_user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=True)
    flagged_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationship to the user who flagged it
    user = relationship("User")
