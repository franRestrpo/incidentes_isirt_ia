"""
Service for dialogue-related operations, like summarization.
"""
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from incident_api import models, schemas
from incident_api.services.llm_service import llm_service
from incident_api.ai.prompt_manager import prompt_manager
from incident_api.services.ai_settings_service import get_active_settings
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)

class DialogueService:
    async def summarize_dialogue(
        self, db: Session, *, conversation_history: List[Dict[str, Any]]
    ) -> schemas.DialogueSummaryResponse:
        """
        Summarizes a conversation history using an LLM.
        """
        ai_settings = get_active_settings(db)
        
        # Format conversation for the prompt
        dialogue_str = "\n".join(
            f"[{msg['sender'].replace('-message', '').upper()}]: {msg['text']}" 
            for msg in conversation_history
        )

        system_prompt = prompt_manager.get_dialogue_summary_prompt(dialogue_str)
        messages = [SystemMessage(content=system_prompt)]

        summary_dict = await llm_service.invoke_for_json(messages, ai_settings)
        
        return schemas.DialogueSummaryResponse(**summary_dict)

dialogue_service = DialogueService()
