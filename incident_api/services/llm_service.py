"""
Servicio para la invocación de modelos de lenguaje (LLM).
"""

import logging
import json
from fastapi import HTTPException, status
from typing import Dict, Any

from incident_api import models
from incident_api.ai.llm_factory import get_llm

logger = logging.getLogger(__name__)


class LLMService:
    """
    Servicio para manejar la comunicación con modelos de lenguaje.
    """

    async def invoke(
        self,
        messages: list,
        settings: models.AIModelSettings
    ) -> str:
        """Invoca al LLM y devuelve la respuesta como string."""
        try:
            llm = get_llm(provider=settings.model_provider, model_name=settings.model_name, parameters=settings.parameters)
            ai_response_message = await llm.ainvoke(messages)
            ai_response = ai_response_message.content if hasattr(ai_response_message, 'content') else ai_response_message
            return ai_response
        except Exception as e:
            logger.error(f"Error al invocar el modelo de IA: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail="Servicio de IA no disponible.")

    async def invoke_for_json(
        self,
        messages: list,
        settings: models.AIModelSettings
    ) -> Dict[str, Any]:
        """Invoca al LLM y parsea la respuesta JSON a un diccionario."""
        try:
            llm = get_llm(provider=settings.model_provider, model_name=settings.model_name, parameters=settings.parameters)
            ai_response = await llm.ainvoke(messages)
            content = ai_response.content.strip()

            if content.startswith("```json"):
                content = content[7:-4].strip()

            data = json.loads(content)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar la respuesta JSON del LLM. Contenido recibido: '{ai_response.content}'", exc_info=True)
            raise HTTPException(status_code=500, detail="Formato de respuesta de IA inválido.")
        except Exception as e:
            logger.error(f"Error al invocar el modelo de IA: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail="Servicio de IA no disponible.")


llm_service = LLMService()