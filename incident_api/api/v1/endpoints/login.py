"""
Endpoints de la API para la autenticación y registro de usuarios.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from incident_api import schemas, models
from incident_api.api import dependencies
from incident_api.core import security
from incident_api.core.config import settings
from incident_api.services import user_service
from incident_api.services.rate_limiting_service import check_login_rate_limit
from incident_api.services.audit_service import AuditService
from incident_api.services.alerting_service import alerting_service

router = APIRouter()


@router.post(
    "/register",
    response_model=schemas.UserInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
)
def register_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(dependencies.get_db),
    admin_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Registra un nuevo usuario en el sistema.

    La lógica de negocio (ej. email único) se maneja en la capa de servicio/CRUD.

    Args:
        user_in (schemas.UserCreate): Datos del nuevo usuario a crear.
        db (Session): Dependencia de la sesión de la base de datos.

    Returns:
        schemas.UserInDB: El usuario recién creado.
    """
    # La comprobación de email duplicado ahora está en la capa CRUD.
    # El servicio simplemente llama al CRUD.
    # Si el email existe, se lanzará una HTTPException desde la capa CRUD.
    logger = logging.getLogger(__name__)
    logger.info(f"Admin user {admin_user.email} creating new user: {user_in.email}")
    new_user = user_service.create_user(db=db, user_in=user_in)
    logger.info(f"User {new_user.email} created successfully.")
    return new_user


@router.post("/token", summary="Autenticar usuario y establecer cookie HttpOnly")
def login_for_access_token(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(dependencies.get_db),
):
    """
    Autentica al usuario y establece un token de acceso JWT en una cookie HttpOnly.

    Args:
        response (Response): Objeto de respuesta para establecer la cookie.
        request (Request): Objeto de solicitud para logging.
        form_data (OAuth2PasswordRequestForm): Formulario con username (email) y password.
        db (Session): Dependencia de la sesión de la base de datos.

    Returns:
        Un mensaje de éxito con información del usuario.
    """
    logger = logging.getLogger(__name__)
    audit_service = AuditService()
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    timestamp = datetime.now().isoformat()

    # Verificar rate limiting antes de procesar
    check_login_rate_limit(request)

    user = security.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        logger.warning(f"Login failed - IP: {client_ip}, Email: {form_data.username}, Reason: Invalid credentials or inactive user")

        # --- INICIO: Alerta y Auditoría de Fallo ---
        alerting_service.trigger_alert(
            message=f"Failed login attempt for email '{form_data.username}' from IP: {client_ip}",
            level="error"
        )
        audit_service.log_action(
            db=db,
            request=request,
            action="LOGIN_FAILURE",
            resource_type="USER_AUTH",
            success=False,
            details={"attempted_email": form_data.username}
        )
        # --- FIN: Alerta y Auditoría de Fallo ---

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos, o usuario inactivo.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Login successful - IP: {client_ip}, Email: {form_data.username}, UserID: {user.user_id}, Role: {user.role}")

    # --- INICIO: Auditoría de Éxito ---
    audit_service.log_action(
        db=db,
        request=request,
        user_id=user.user_id,
        action="LOGIN_SUCCESS",
        resource_type="USER_AUTH",
        success=True
    )
    # --- FIN: Auditoría de Éxito ---

    access_token = security.create_access_token(data={"sub": user.email})

    is_production = settings.ENVIRONMENT == "production"
    cookie_secure = is_production
    cookie_samesite = "none" if is_production else "lax"

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        secure=cookie_secure,
        samesite=cookie_samesite
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login successful",
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@router.post("/logout", summary="Cerrar sesión del usuario")
def logout_user(response: Response):
    """
    Cierra la sesión del usuario eliminando la cookie HttpOnly.

    Returns:
        Un mensaje de éxito.
    """
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True
    )
    return {"message": "Logout successful"}


@router.get("/debug", summary="Información de debugging del sistema", tags=["Debug"])
def get_debug_info(request: Request):
    """
    Proporciona información de debugging del sistema (solo en desarrollo).

    Returns:
        Información del sistema para troubleshooting.
    """
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Endpoint de debugging solo disponible en modo desarrollo."
        )

    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    cookies = request.cookies

    return {
        "timestamp": datetime.now().isoformat(),
        "environment": "development",
        "client_ip": client_ip,
        "user_agent": user_agent,
        "cookies": {k: "***" if "token" in k.lower() else v for k, v in cookies.items()},
        "server_info": {
            "debug_mode": settings.DEBUG,
            "project_name": settings.PROJECT_NAME,
            "project_version": settings.PROJECT_VERSION,
            "token_expiration_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        },
    }