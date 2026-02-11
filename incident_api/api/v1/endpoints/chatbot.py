"""
Endpoints de la API para la interacción con el Chatbot de IA.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from incident_api import schemas, models
from incident_api.api import dependencies
from incident_api.services.chat_service import chat_service
from incident_api.services.conversation_history_service import conversation_history_service
from incident_api.services.ai_settings_service import get_active_settings

router = APIRouter()


@router.post(
    "/ask", response_model=schemas.ChatbotResponse, summary="Enviar mensaje al chatbot"
)
async def ask_chatbot(
    request: schemas.ChatbotRequest,
    db: Session = Depends(dependencies.get_db),
    irt_user: models.User = Depends(dependencies.get_current_irt_user),
):
    """
    Procesa un mensaje del usuario, lo envía al servicio de IA y devuelve una respuesta.

    Esta operación requiere que el usuario sea un miembro del equipo de respuesta
    a incidentes (IRT). La conversación se mantiene a través del `conversation_id`.

    Args:
        request (schemas.ChatRequest): La petición con el prompt y el ID de conversación.
        db (Session): Dependencia de la sesión de la base de datos.
        irt_user (models.User): Dependencia que valida los permisos de IRT.

    Returns:
        schemas.ChatResponse: La respuesta del asistente y el ID de conversación.
    """
    if not request.prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El mensaje no puede estar vacío.",
        )

    try:
        logger.info(f"Solicitud de chatbot recibida - Usuario: {irt_user.user_id}, Conversación: {request.conversation_id}")
        logger.debug(f"Prompt recibido: {request.prompt[:100]}...")

        ai_settings = get_active_settings(db)
        if not ai_settings:
            logger.warning(f"Configuración de IA no encontrada para usuario {irt_user.user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La configuración del modelo de IA no ha sido establecida."
            )

        logger.debug(f"Usando configuración de IA: {ai_settings.model_provider} - {ai_settings.model_name}")

        ai_response = await chat_service.get_isirt_assistant_response(
            db, request.prompt, request.conversation_id, irt_user.user_id, settings=ai_settings, is_start_of_conversation=request.is_start_of_conversation
        )

        logger.info(f"Respuesta de chatbot generada exitosamente - Usuario: {irt_user.user_id}, Longitud: {len(ai_response)} caracteres")

        return schemas.ChatbotResponse(
            response=ai_response, conversation_id=request.conversation_id
        )
    except HTTPException as e: # Capturar HTTPException directamente
        logger.warning(f"HTTPException en chatbot - Usuario: {irt_user.user_id}, Código: {e.status_code}, Detalle: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error inesperado en el endpoint del chatbot - Usuario: {irt_user.user_id}, Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error interno en el servidor de IA.",
        )


@router.get(
    "/history/{conversation_id}",
    response_model=schemas.ConversationHistoryInDB,
    summary="Obtener historial de conversación",
)
def get_conversation_history(
    conversation_id: str,
    db: Session = Depends(dependencies.get_db),
    irt_user: models.User = Depends(dependencies.get_current_irt_user),
):
    """
    Obtiene el historial completo de mensajes de una conversación específica.

    Requiere que el usuario sea un miembro del equipo de respuesta a incidentes (IRT).

    Args:
        conversation_id (str): El ID de la conversación a recuperar.
        db (Session): Dependencia de la sesión de la base de datos.
        irt_user (models.User): Dependencia que valida los permisos de IRT.

    Returns:
        schemas.ConversationHistoryInDB: El historial de la conversación.
    """
    history = conversation_history_service.get_history_messages(db, conversation_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Historial de conversación no encontrado.",
        )
    return history