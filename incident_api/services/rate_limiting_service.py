"""
Servicio de rate limiting para proteger contra ataques de fuerza bruta.

Implementa diferentes estrategias de rate limiting para diferentes endpoints.
"""

import time
import logging
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import HTTPException, Request, status

from incident_api.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Excepción lanzada cuando se excede el límite de rate."""
    pass


class RateLimitingService:
    """
    Servicio para implementar rate limiting basado en memoria.

    En producción, considera usar Redis u otra solución distribuida.
    """

    def __init__(self):
        # Estructura: {ip_or_key: [(timestamp, count), ...]}
        self._attempts: Dict[str, list] = defaultdict(list)
        self._cleanup_interval = 300  # 5 minutos

    def _cleanup_old_attempts(self, key: str) -> None:
        """Limpia intentos antiguos para una clave específica."""
        current_time = time.time()
        cutoff_time = current_time - self._cleanup_interval

        self._attempts[key] = [
            (timestamp, count) for timestamp, count in self._attempts[key]
            if timestamp > cutoff_time
        ]

        # Remover clave si no hay intentos
        if not self._attempts[key]:
            del self._attempts[key]

    def _get_attempts_in_window(self, key: str, window_seconds: int) -> int:
        """Obtiene el número de intentos en la ventana de tiempo especificada."""
        current_time = time.time()
        cutoff_time = current_time - window_seconds

        return sum(
            count for timestamp, count in self._attempts[key]
            if timestamp > cutoff_time
        )

    def check_rate_limit(
        self,
        key: str,
        max_attempts: int,
        window_seconds: int,
        block_duration: int = 0
    ) -> None:
        """
        Verifica si una clave excede el límite de rate.

        Args:
            key: Identificador único (ej. IP address)
            max_attempts: Número máximo de intentos permitidos
            window_seconds: Ventana de tiempo en segundos
            block_duration: Duración del bloqueo en segundos (0 = no bloquear)

        Raises:
            RateLimitExceeded: Si se excede el límite
        """
        self._cleanup_old_attempts(key)

        attempts = self._get_attempts_in_window(key, window_seconds)

        if attempts >= max_attempts:
            if block_duration > 0:
                # Agregar bloqueo temporal
                block_until = time.time() + block_duration
                self._attempts[key].append((block_until, max_attempts + 1))

            logger.warning(f"Rate limit exceeded for key: {key}, attempts: {attempts}")
            raise RateLimitExceeded(
                f"Demasiados intentos. Máximo {max_attempts} por {window_seconds} segundos."
            )

        # Registrar el intento
        self._attempts[key].append((time.time(), 1))

    def is_blocked(self, key: str) -> bool:
        """Verifica si una clave está bloqueada temporalmente."""
        current_time = time.time()
        self._cleanup_old_attempts(key)

        for timestamp, count in self._attempts[key]:
            if timestamp > current_time and count > 0:
                return True
        return False


# Instancia global del servicio
rate_limiter = RateLimitingService()


def check_login_rate_limit(request: Request) -> None:
    """
    Verifica el rate limiting para endpoints de login.

    Args:
        request: Objeto de solicitud FastAPI

    Raises:
        HTTPException: Si se excede el límite
    """
    client_ip = request.client.host if request.client else "unknown"

    # Verificar si está bloqueado
    if rate_limiter.is_blocked(client_ip):
        logger.warning(f"Blocked IP attempting login: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Cuenta temporalmente bloqueada por demasiados intentos fallidos.",
            headers={"Retry-After": str(settings.LOGIN_LOCKOUT_MINUTES * 60)}
        )

    try:
        rate_limiter.check_rate_limit(
            key=client_ip,
            max_attempts=settings.LOGIN_MAX_ATTEMPTS,
            window_seconds=settings.LOGIN_RATE_LIMIT_WINDOW_MINUTES * 60,
            block_duration=settings.LOGIN_LOCKOUT_MINUTES * 60
        )
    except RateLimitExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
            headers={"Retry-After": str(settings.LOGIN_LOCKOUT_MINUTES * 60)}
        )


def check_oauth_rate_limit(request: Request) -> None:
    """
    Verifica el rate limiting para endpoints OAuth.

    Args:
        request: Objeto de solicitud FastAPI

    Raises:
        HTTPException: Si se excede el límite
    """
    client_ip = request.client.host if request.client else "unknown"

    try:
        # Límite más permisivo para OAuth durante desarrollo
        rate_limiter.check_rate_limit(
            key=f"oauth_{client_ip}",
            max_attempts=10,  # Máximo 10 intentos OAuth por ventana
            window_seconds=600,  # 10 minutos
            block_duration=300  # Bloqueo de 5 minutos
        )
    except RateLimitExceeded as e:
        logger.warning(f"OAuth rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos de autenticación OAuth. Intente más tarde.",
            headers={"Retry-After": "300"}
        )


def check_audit_rate_limit(request: Request) -> None:
    """
    Verifica el rate limiting para endpoints de auditoría.

    Args:
        request: Objeto de solicitud FastAPI

    Raises:
        HTTPException: Si se excede el límite
    """
    client_ip = request.client.host if request.client else "unknown"

    try:
        # Límite más flexible para auditoría: 30 consultas por minuto por IP
        rate_limiter.check_rate_limit(
            key=f"audit_{client_ip}",
            max_attempts=30,
            window_seconds=60,  # 1 minuto
            block_duration=300  # Bloqueo de 5 minutos
        )
    except RateLimitExceeded as e:
        logger.warning(f"Audit rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiadas consultas de auditoría. Intente más tarde.",
            headers={"Retry-After": "1800"}
        )