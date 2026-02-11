"""Módulo para la gestión de seguridad: hashing de contraseñas, creación y verificación de tokens JWT."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict

from fastapi import HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from incident_api.core.config import settings
from incident_api.core.hashing import Hasher
from incident_api import crud, models


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un nuevo token de acceso JWT.

    Args:
        data: Datos a incluir en el payload del token (ej. {"sub": user.email}).
        expires_delta: Duración opcional del token. Si no se proporciona, usa la configuración por defecto.

    Returns:
        El token JWT codificado como una cadena.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """
    Autentica a un usuario de forma segura, mitigando ataques de enumeración de usuarios.

    Verifica las credenciales y si el usuario está activo. El tiempo de ejecución es
    constante para evitar ataques de temporización.

    Args:
        db: La sesión de la base de datos.
        email: El correo electrónico del usuario.
        password: La contraseña en texto plano proporcionada por el usuario.

    Returns:
        El objeto User si la autenticación es exitosa, de lo contrario None.
    """
    logger = logging.getLogger(__name__)

    user = crud.user.get_by_email(db, email=email)

    # Si el usuario no existe o no está activo, usamos un hash falso para la verificación.
    # Esto asegura que la función de verificación de hash se ejecute siempre,
    # haciendo que el tiempo de respuesta sea similar al de un login fallido normal.
    if not user or not user.is_active:
        # Hash de una contraseña conocida imposible para asegurar que la verificación falle.
        dummy_hash = Hasher.get_password_hash("invalid_password_for_timing_attack_mitigation")
        Hasher.verify_password(password, dummy_hash)
        
        if settings.DEBUG or logger.isEnabledFor(logging.DEBUG):
            if not user:
                logger.debug(f"Authentication failed: User not found - {email}")
            else: # User is inactive
                logger.debug(f"Authentication failed: Inactive user - {email}")
        return None

    # Verificar la contraseña real
    if not Hasher.verify_password(password, user.hashed_password):
        if settings.DEBUG or logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Authentication failed: Invalid password for user - {email}")
        return None

    # Usuario autenticado exitosamente
    if settings.DEBUG or logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"User authenticated successfully: {email} (ID: {user.user_id})")

    return user


def get_user_from_token(db: Session, token: str, credentials_exception: HTTPException) -> models.User:
    """
    Decodifica un token JWT, valida su payload y obtiene el usuario correspondiente.

    Args:
        db: La sesión de la base de datos.
        token: El token JWT a decodificar.
        credentials_exception: La excepción a lanzar si la validación falla.

    Returns:
        El objeto User si el token es válido y el usuario existe.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.user.get_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user
