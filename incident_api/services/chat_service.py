"""
Servicio para la lógica de negocio relacionada con el chatbot de IA.
"""

import logging
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from incident_api import crud, schemas, models
from incident_api.services.conversation_history_service import conversation_history_service
from incident_api.services.llm_service import llm_service
from incident_api.services.rag_retrieval_service import rag_retrieval_service
from incident_api.services.ai_text_utils import sanitize_for_prompt

logger = logging.getLogger(__name__)


class ChatService:
    """
    Clase de servicio para gestionar la lógica de negocio del chatbot.
    """


    def _build_prompt_messages(
        self,
        system_prompt: str,
        context: str,
        history: List[models.ConversationHistory],
        user_prompt: str
    ) -> List:
        """Construye la lista de mensajes estructurados para el modelo de IA."""
        logger.info("--- Using System Prompt for AI call ---")
        logger.info(f"{system_prompt[:250]}...")
        logger.info("------------------------------------")

        messages = [SystemMessage(content=sanitize_for_prompt(system_prompt))]
        
        if context:
            messages.append(SystemMessage(content=f"Usa el siguiente contexto de los playbooks para responder:\n{sanitize_for_prompt(context)}"))

        for entry in history:
            if entry.role == "user":
                messages.append(HumanMessage(content=sanitize_for_prompt(entry.message_content)))
            else:
                messages.append(AIMessage(content=sanitize_for_prompt(entry.message_content)))

        if user_prompt:
              messages.append(HumanMessage(content=sanitize_for_prompt(user_prompt)))
        
        return messages

    async def _prepare_context(self, use_rag: bool, prompt: str) -> str:
        """Prepara el contexto usando RAG si es necesario."""
        if use_rag:
            return await rag_retrieval_service.retrieve_context(prompt)
        return ""

    def _prepare_messages(
        self,
        system_prompt: str,
        context: str,
        history: List[models.ConversationHistory],
        user_prompt: str,
        is_start_of_conversation: bool
    ) -> List:
        """Construye la lista de mensajes estructurados para el modelo de IA."""
        return self._build_prompt_messages(
            system_prompt=system_prompt,
            context=context,
            history=history,
            user_prompt=user_prompt if not is_start_of_conversation else None,
        )

    async def _invoke_llm(self, messages: List, settings: models.AIModelSettings) -> str:
        """Invoca al LLM con los mensajes preparados."""
        return await llm_service.invoke(messages, settings)

    def _save_response(self, db: Session, conversation_id: str, user_id: int, ai_response: str):
        """Guarda la respuesta del asistente en el historial."""
        conversation_history_service.save_message(db, conversation_id, user_id, "assistant", ai_response)

    async def _get_assistant_response(
        self,
        db: Session,
        prompt: str,
        conversation_id: str,
        user_id: int,
        settings: models.AIModelSettings,
        system_prompt: str,
        use_rag: bool,
        is_start_of_conversation: bool = False
    ) -> str:
        """Método unificado para obtener respuestas del asistente de IA."""
        rag_context = await self._prepare_context(use_rag, prompt)

        if prompt and not is_start_of_conversation:
            conversation_history_service.save_message(db, conversation_id, user_id, "user", prompt)

        history = conversation_history_service.get_history_messages(db, conversation_id)

        messages = self._prepare_messages(system_prompt, rag_context, history, prompt, is_start_of_conversation)

        ai_response = await self._invoke_llm(messages, settings)

        self._save_response(db, conversation_id, user_id, ai_response)
        return ai_response

    async def get_reporting_assistant_response(
        self,
        db: Session,
        prompt: str,
        conversation_id: str,
        user_id: int,
        settings: models.AIModelSettings,
        is_start_of_conversation: bool = False
    ) -> str:
        """
        Orquesta la obtención de una respuesta del asistente de REPORTE de incidentes (SecBot).
        """
        return await self._get_assistant_response(
            db=db,
            prompt=prompt,
            conversation_id=conversation_id,
            user_id=user_id,
            settings=settings,
            system_prompt=settings.system_prompt,
            use_rag=False,
            is_start_of_conversation=is_start_of_conversation
        )

    async def get_isirt_assistant_response(
        self,
        db: Session,
        prompt: str,
        conversation_id: str,
        user_id: int,
        settings: models.AIModelSettings,
        is_start_of_conversation: bool = False
    ) -> str:
        """
        Orquesta la obtención de una respuesta del asistente para el EQUIPO ISIRT.
        """
        logger.info(f"Solicitando respuesta del asistente ISIRT - Usuario: {user_id}, Conversación: {conversation_id}")
        logger.debug(f"Prompt del usuario: {prompt[:100]}...")

        response = await self._get_assistant_response(
            db=db,
            prompt=prompt,
            conversation_id=conversation_id,
            user_id=user_id,
            settings=settings,
            system_prompt=settings.isirt_prompt,
            use_rag=True,
            is_start_of_conversation=is_start_of_conversation
        )

        logger.info(f"Respuesta del asistente ISIRT generada exitosamente - Longitud: {len(response)} caracteres")
        return response

chat_service = ChatService()