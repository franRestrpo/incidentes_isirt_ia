"""
API endpoints for RAG-related operations, such as knowledge curation.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from incident_api import crud, schemas
from incident_api.api import dependencies
from incident_api.models.user import User

router = APIRouter()

class CurationRequest(schemas.BaseModel):
    source_name: str
    chunk_id: str
    notes: Optional[str] = None

@router.post("/curate", status_code=200)
def flag_knowledge_chunk(
    *,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
    curation_in: CurationRequest
):
    """
    Flag a knowledge chunk as incorrect or obsolete.
    
    This endpoint allows an authenticated user to provide feedback on a specific
    piece of knowledge retrieved by the RAG.
    """
    # Find if a record already exists
    db_obj = crud.knowledge_curation.get_by_source_and_chunk(
        db, source_name=curation_in.source_name, chunk_id=curation_in.chunk_id
    )
    
    if db_obj:
        # Update existing record
        update_data = {
            "status": "flagged",
            "flagged_by_user_id": current_user.user_id,
            "flagged_at": datetime.utcnow(),
            "notes": db_obj.notes + f"\n---\nFeedback from {current_user.email} at {datetime.utcnow()}:\n{curation_in.notes}" if db_obj.notes else f"Feedback from {current_user.email} at {datetime.utcnow()}:\n{curation_in.notes}"
        }
        crud.knowledge_curation.update(db, db_obj=db_obj, obj_in=update_data)
    else:
        # Create new record
        create_data = schemas.KnowledgeCurationCreate(
            source_name=curation_in.source_name,
            chunk_id=curation_in.chunk_id,
            status="flagged",
            flagged_by_user_id=current_user.user_id,
            notes=f"Feedback from {current_user.email} at {datetime.utcnow()}:\n{curation_in.notes}"
        )
        crud.knowledge_curation.create(db, obj_in=create_data)
        
    return {"message": "Knowledge chunk flagged successfully. It will be excluded from future suggestions pending review."}
