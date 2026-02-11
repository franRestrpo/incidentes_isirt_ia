"""
Decoradores personalizados para la API.

Este módulo contiene decoradores que añaden funcionalidades transversales
a los endpoints de la API, como el registro de auditoría.
"""

import functools
import inspect
import logging
from typing import Any, Callable, Optional, Dict, Set
from pydantic import BaseModel

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session, DeclarativeMeta

from incident_api.api import dependencies
from incident_api.models.user import User, UserRole
from incident_api.services.audit_service import AuditService
from incident_api.services.alerting_service import alerting_service

logger = logging.getLogger(__name__)

# --- INICIO: Lógica de Alerta de Escalada de Privilegios ---

ADMIN_ROLES: Set[str] = {UserRole.ADMINISTRADOR, UserRole.SUPER_ADMIN}

def _check_for_privilege_escalation(
    changes: Dict[str, Any],
    resource_id: Optional[int],
    auditing_user: User
) -> None:
    """
    Inspecciona los cambios de un recurso y dispara una alerta si detecta una escalada de privilegios.
    """
    if not changes or not resource_id:
        return

    old_values = changes.get("old_values", {})
    new_values = changes.get("new_values", {})

    if "role" in new_values:
        old_role = old_values.get("role")
        new_role = new_values.get("role")

        is_escalation = new_role in ADMIN_ROLES and old_role not in ADMIN_ROLES

        if is_escalation:
            alert_message = (
                f"SECURITY ALERT: Privilege escalation detected for user ID '{resource_id}'. "
                f"Role changed from '{old_role}' to '{new_role}' by user '{auditing_user.email}' (ID: {auditing_user.user_id})."
            )
            alerting_service.trigger_alert(alert_message, level="critical")

def _check_for_admin_deactivation(
    changes: Dict[str, Any],
    old_state: Dict[str, Any],
    resource_id: Optional[int],
    auditing_user: User
) -> None:
    """
    Inspecciona los cambios y dispara una alerta si se desactiva una cuenta de administrador.
    """
    if not all([changes, old_state, resource_id]):
        return

    new_values = changes.get("new_values", {})
    if new_values.get("is_active") is False and old_state.get("role") in ADMIN_ROLES:
        alert_message = (
            f"SECURITY ALERT: Administrator account deactivated. User '{old_state.get('email')}' (ID: {resource_id}) "
            f"was deactivated by user '{auditing_user.email}' (ID: {auditing_user.user_id})."
        )
        alerting_service.trigger_alert(alert_message, level="critical")

# --- FIN: Lógica de Alerta de Escalada de Privilegios ---


# Campos sensibles que nunca deben ser incluidos en los logs de auditoría.
SENSITIVE_FIELDS: Set[str] = {
    "hashed_password",
    "password",
    "token",
    "access_token",
    "refresh_token",
}


def _model_to_dict(model: Any) -> Dict[str, Any]:
    """Convierte un modelo SQLAlchemy o Pydantic a un diccionario."""
    if isinstance(model, BaseModel):
        return model.model_dump()
    if hasattr(model, '__table__'):  # Asume que es un modelo SQLAlchemy
        return {c.name: getattr(model, c.name) for c in model.__table__.columns}
    return {}


def _get_diff(
    old_dict: Dict[str, Any], new_dict: Dict[str, Any], exclude: Set[str]
) -> Dict[str, Any]:
    """
    Compara dos diccionarios y devuelve las diferencias, excluyendo campos sensibles.
    """
    diff = {"old_values": {}, "new_values": {}}
    all_keys = old_dict.keys() | new_dict.keys()

    for key in all_keys:
        if key in exclude:
            continue

        old_value = old_dict.get(key)
        new_value = new_dict.get(key)

        if old_value != new_value:
            diff["old_values"][key] = old_value
            diff["new_values"][key] = new_value

    return diff if diff["old_values"] or diff["new_values"] else {}


def audit_action(
    action: str,
    resource_type: str,
    resource_id_param: Optional[str] = None,
    get_resource_func: Optional[Callable] = None,
) -> Callable:
    """
    Decorador para registrar una acción de auditoría en un endpoint de FastAPI.

    Permite registrar cambios de datos detallados (antes y después) y detectar escalada de privilegios.

    Args:
        action (str): El nombre de la acción (e.g., 'UPDATE_USER').
        resource_type (str): El tipo de recurso (e.g., 'USER').
        resource_id_param (str, optional): El nombre del parámetro que contiene el ID del recurso.
        get_resource_func (Callable, optional): Una función que, dado un `db` y un `id`,
            devuelve el estado del recurso ANTES de la modificación.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            db: Optional[Session] = kwargs.get("db")
            current_user: Optional[User] = kwargs.get("current_user")
            request: Optional[Request] = kwargs.get("request")
            audit_service = AuditService()

            if not all([db, current_user, request]):
                logger.error(
                    "Audit decorator on '%s' is missing dependencies.", func.__name__
                )
                return await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)

            resource_id: Optional[int] = kwargs.get(resource_id_param) if resource_id_param else None
            old_state: Optional[Dict[str, Any]] = None
            details: Dict[str, Any] = {}

            # Obtener estado "antes" si es una operación de actualización/borrado
            if get_resource_func and resource_id:
                try:
                    old_resource = get_resource_func(db, id=resource_id)
                    if old_resource:
                        old_state = _model_to_dict(old_resource)
                except Exception as e:
                    logger.error("Failed to get old state in audit decorator: %s", e)

            try:
                response = await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)

                # Extraer ID de la respuesta para operaciones de CREACIÓN
                if not resource_id:
                    if hasattr(response, "id"):
                        resource_id = getattr(response, "id")
                    elif hasattr(response, "user_id"):
                        resource_id = getattr(response, "user_id")

                # Calcular diff y comprobar alertas si es una actualización
                if old_state:
                    new_state = _model_to_dict(response)
                    changes = _get_diff(old_state, new_state, exclude=SENSITIVE_FIELDS)
                    if changes:
                        details = {"changes": changes}
                        # Comprobar si el cambio de datos constituye una alerta de seguridad
                        if resource_type == "USER":
                            _check_for_privilege_escalation(details.get("changes", {}), resource_id, current_user)
                            _check_for_admin_deactivation(details.get("changes", {}), old_state, resource_id, current_user)
                    else:
                        details = {"response": "Action completed successfully (no data changed)."}
                else:
                    details = {"response": "Action completed successfully."}

                audit_service.log_action(
                    db=db,
                    user_id=current_user.user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    request=request,
                    success=True,
                    details=details,
                )
                return response

            except Exception as e:
                error_details = {"error": type(e).__name__, "detail": str(e)}
                if isinstance(e, HTTPException):
                    error_details["status_code"] = e.status_code

                logger.error(
                    "Exception in audited endpoint '%s': %s", func.__name__, e, exc_info=True
                )
                audit_service.log_action(
                    db=db,
                    user_id=current_user.user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    request=request,
                    success=False,
                    details=error_details,
                )
                raise

        return wrapper
    return decorator
