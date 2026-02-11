"""
Endpoints para la autenticación con Google OAuth2.

Este módulo delega la lógica de negocio al servicio GoogleOAuthService,
siguiendo el principio de responsabilidad única.
"""

import logging
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from incident_api.core import security
from incident_api.core.config import settings
from incident_api.api import dependencies
from incident_api import schemas
from incident_api.services.google_oauth_service import GoogleOAuthService
from incident_api.services.rate_limiting_service import check_oauth_rate_limit

from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class GoogleTokenRequest(BaseModel):
    """Modelo para la solicitud de intercambio de código OAuth."""
    code: str
    redirect_uri: str


@router.get("/google", summary="Redirigir a Google para autenticación")
async def login_google(request: Request):
    """
    Redirige al usuario a la pantalla de consentimiento de Google OAuth2.

    Returns:
        Response: Redirección HTTP a Google OAuth.
    """
    auth_url = GoogleOAuthService.build_auth_url()
    logger.info(f"Redirecting user to Google OAuth: {request.client.host if request.client else 'unknown'}")
    return Response(status_code=status.HTTP_302_FOUND, headers={"Location": auth_url})


@router.post("/google/exchange-code", response_model=schemas.UserInDB, summary="Intercambiar código de Google por token de sesión")
async def google_exchange_code(
    token_request: GoogleTokenRequest,
    request: Request,
    response: Response,
    db: Session = Depends(dependencies.get_db)
):
    """
    Maneja el callback de Google después de la autenticación del usuario.
    Intercambia el código por un token, valida la información del usuario,
    crea o actualiza el usuario en la base de datos y establece una sesión.

    Args:
        token_request: Datos del código OAuth y redirect URI.
        request: Objeto de solicitud HTTP.
        response: Objeto de respuesta HTTP.
        db: Sesión de base de datos.

    Returns:
        User: Información del usuario autenticado.
    """
    client_ip = request.client.host if request.client else "unknown"

    # Verificar rate limiting para OAuth
    check_oauth_rate_limit(request)

    logger.info(f"OAuth code exchange attempt from IP: {client_ip}")

    try:
        # Intercambiar código por token
        token_data = await GoogleOAuthService.exchange_code_for_token(
            token_request.code, token_request.redirect_uri
        )

        # Obtener información del usuario
        user_info = await GoogleOAuthService.get_user_info(token_data["access_token"])

        # Validar información del usuario
        GoogleOAuthService.validate_user_info(user_info)

        # Buscar o crear usuario
        user = GoogleOAuthService.find_or_create_user(db, user_info)

        # Crear token de aplicación
        app_access_token = security.create_access_token(data={"sub": user.email})

        # Configurar cookie de sesión
        is_production = settings.ENVIRONMENT == "production"
        cookie_secure = is_production
        cookie_samesite = "none" if is_production else "lax"

        response.set_cookie(
            key="access_token",
            value=app_access_token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
            secure=cookie_secure,
            samesite=cookie_samesite
        )

        logger.info(f"OAuth login successful for user: {user.email} (ID: {user.user_id}) from IP: {client_ip}")
        return user

    except Exception as e:
        email = "unknown"
        if "user_info" in locals() and hasattr(user_info, "email"):
            email = user_info.email
        logger.warning(f"OAuth login failed for user {email} from IP {client_ip}: {str(e)}")
        raise
