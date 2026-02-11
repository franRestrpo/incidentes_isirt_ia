"""
Servicio para manejar la autenticación OAuth2 con Google.

Este servicio encapsula toda la lógica relacionada con Google OAuth2,
siguiendo el principio de responsabilidad única.
"""

import logging
from typing import Dict, Optional, Any
import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from incident_api.core.config import settings
from incident_api import crud, models
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class GoogleUserInfo(BaseModel):
    """Modelo para la información del usuario obtenida de Google."""
    sub: str
    email: str
    email_verified: bool
    name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None


class GoogleOAuthService:
    """Servicio para manejar operaciones OAuth2 con Google."""

    @staticmethod
    def validate_google_config() -> None:
        """Valida que la configuración de Google OAuth esté completa."""
        required_settings = [
            settings.GOOGLE_CLIENT_ID,
            settings.GOOGLE_CLIENT_SECRET,
            settings.GOOGLE_REDIRECT_URI
        ]

        if not all(required_settings):
            logger.error("Configuración de Google OAuth incompleta")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="La configuración de Google OAuth2 está incompleta en el servidor.",
            )

    @staticmethod
    def build_auth_url() -> str:
        """Construye la URL de autorización de Google."""
        GoogleOAuthService.validate_google_config()

        return (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.GOOGLE_CLIENT_ID}&"
            f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
            f"response_type=code&"
            f"scope=openid%20email%20profile&"
            f"access_type=offline&"
            f"prompt=consent"
        )

    @staticmethod
    async def exchange_code_for_token(code: str, redirect_uri: str) -> Dict[str, Any]:
        """Intercambia el código de autorización por un token de acceso."""
        GoogleOAuthService.validate_google_config()

        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(token_url, data=token_data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error exchanging code for token: {e.response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error al intercambiar el código de autorización: {e.response.status_code}",
                )
            except Exception as e:
                logger.error(f"Unexpected error during token exchange: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error interno del servidor durante la autenticación.",
                )

    @staticmethod
    async def get_user_info(access_token: str) -> GoogleUserInfo:
        """Obtiene la información del usuario desde Google."""
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(user_info_url, headers=headers)
                response.raise_for_status()
                user_data = response.json()
                return GoogleUserInfo(**user_data)
            except httpx.HTTPStatusError as e:
                logger.error(f"Error getting user info: {e.response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error al obtener la información del usuario: {e.response.status_code}",
                )
            except Exception as e:
                logger.error(f"Unexpected error getting user info: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error interno del servidor al obtener información del usuario.",
                )

    @staticmethod
    def validate_user_info(user_info: GoogleUserInfo) -> None:
        """Valida la información del usuario obtenida de Google."""
        if not user_info.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo obtener el email desde el perfil de Google.",
            )

        if not user_info.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email de Google no está verificado.",
            )

    @staticmethod
    def find_or_create_user(db: Session, user_info: GoogleUserInfo) -> models.User:
        """Busca un usuario existente o crea uno nuevo basado en la info de Google."""
        user = crud.user.get_by_email(db, email=user_info.email)

        if user:
            # Si el usuario ya existe, lo retornamos, "linkeando" la cuenta de Google.
            # La lógica anterior prevenía esto si el usuario tenía contraseña.
            return user

        # Crear nuevo usuario OAuth
        db_user = models.User(
            email=user_info.email,
            full_name=user_info.name,
            hashed_password=None,  # Usuario OAuth no tiene contraseña
            role=models.UserRole.EMPLEADO,
            is_active=True
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"Nuevo usuario OAuth creado: {user_info.email} (ID: {db_user.user_id})")
        return db_user