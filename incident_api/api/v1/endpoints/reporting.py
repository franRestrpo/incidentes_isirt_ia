"""
Endpoints de la API para la interacción con el Chatbot de Reporte de Incidentes (SecBot).
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from incident_api import schemas, models
from incident_api.api import dependencies
from incident_api.services.chat_service import chat_service
from incident_api.services.ai_settings_service import get_active_settings

router = APIRouter()

@router.post(
    "/ask", 
    response_model=schemas.ChatbotResponse, 
    summary="Enviar mensaje a SecBot para reportar un incidente"
)
async def ask_reporting_chatbot(
    request: schemas.ChatbotRequest,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    Procesa un mensaje del usuario durante el reporte de un incidente.
    """
    if not request.prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El mensaje no puede estar vacío.",
        )

    try:
        ai_settings = get_active_settings(db)
        if not ai_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="La configuración del modelo de IA no ha sido establecida."
            )

        # Llama a la función específica para el asistente de reporte
        ai_response = await chat_service.get_reporting_assistant_response(
            db, request.prompt, request.conversation_id, current_user.user_id, settings=ai_settings
        )
        return schemas.ChatbotResponse(
            response=ai_response, conversation_id=request.conversation_id
        )
    except Exception:
        logging.exception("Error inesperado en el endpoint del chatbot de reporte.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error interno en el servidor de IA.",
        )
