"""
API endpoints for incident reporting-related tasks, like summarization.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from incident_api import schemas
from incident_api.api import dependencies
from incident_api.services.dialogue_service import dialogue_service

router = APIRouter()

@router.post(
    "/summarize",
    response_model=schemas.DialogueSummaryResponse,
    summary="Summarize Incident Dialogue",
)
async def summarize_dialogue(
    dialogue_in: schemas.DialogueSummaryRequest,
    db: Session = Depends(dependencies.get_db),
):
    """
    Receives a conversation history and returns a structured summary.
    """
    return await dialogue_service.summarize_dialogue(
        db=db, conversation_history=dialogue_in.conversation_history
    )
