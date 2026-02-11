"""
Pydantic schemas for the Knowledge Curation feature.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base properties shared by all schemas
class KnowledgeCurationBase(BaseModel):
    source_name: str
    chunk_id: str
    status: Optional[str] = "active"
    notes: Optional[str] = None

# Properties to receive on item creation
class KnowledgeCurationCreate(KnowledgeCurationBase):
    flagged_by_user_id: int

# Properties to receive on item update
class KnowledgeCurationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

# Properties shared by models stored in DB
class KnowledgeCurationInDBBase(KnowledgeCurationBase):
    id: int
    flagged_by_user_id: Optional[int] = None
    flagged_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Properties to return to client
class KnowledgeCuration(KnowledgeCurationInDBBase):
    pass

# Properties stored in DB
class KnowledgeCurationInDB(KnowledgeCurationInDBBase):
    pass
