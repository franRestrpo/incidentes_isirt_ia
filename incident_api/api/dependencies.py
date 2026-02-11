"""
Dependencias de FastAPI para la inyección de base de datos y autenticación.
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from incident_api import crud, schemas, models
from incident_api.core.config import settings
from incident_api.core.security import get_user_from_token
from incident_api.db.database import SessionLocal
from incident_api.models import UserRole


# Cookie-based authentication - no longer using OAuth2PasswordBearer


def get_db():
    """
    Dependencia para obtener una sesión de base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_active_user(
    request: Request, db: Session = Depends(get_db)
) -> models.User:
    """
    Obtiene el token JWT de las cookies, lo valida y devuelve el usuario activo.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.cookies.get("access_token")
    if token is None:
        raise credentials_exception

    user = get_user_from_token(db, token, credentials_exception)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return user


def get_current_admin_user(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """
    Verifica si el usuario actual es un Administrador.
    Si no lo es, lanza una excepción HTTP 403.
    """
    if current_user.role != UserRole.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acción reservada para administradores.",
        )
    return current_user


def get_current_super_admin_user(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """
    Verifica si el usuario actual es un Super Admin.
    Si no lo es, lanza una excepción HTTP 403.
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acción reservada para super administradores.",
        )
    return current_user


def get_current_audit_user(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """
    Verifica si el usuario actual puede realizar auditorías (Admin o Super Admin).
    """
    if current_user.role not in [UserRole.ADMINISTRADOR, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acción reservada para administradores.",
        )
    return current_user


def get_current_irt_user(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """
    Verifica si el usuario actual es un miembro del IRT o un Administrador.
    Si no lo es, lanza una excepción HTTP 403.
    """
    if current_user.role not in [
        UserRole.MIEMBRO_IRT,
        UserRole.LIDER_IRT,
        UserRole.ADMINISTRADOR,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acción reservada para miembros del equipo de respuesta a incidentes.",
        )
    return current_user


def get_incident_or_404(
    incident_id: int, db: Session = Depends(get_db)
) -> models.Incident:
    """
    Obtiene un incidente por su ID o devuelve un error 404 si no se encuentra.
    """
    incident = crud.incident.get(db, id=incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incidente no encontrado."
        )
    return incident


def get_incident_with_permission(
    incident: models.Incident = Depends(get_incident_or_404),
    current_user: models.User = Depends(get_current_active_user),
) -> models.Incident:
    """
    Obtiene un incidente y verifica si el usuario actual tiene permisos para acceder a él.

    Permite el acceso si el usuario es el reportante, el asignado, o tiene un rol de IRT.
    """
    # El chequeo de 'is_active' ya está en get_current_active_user
    is_reporter = current_user.user_id == incident.reported_by_id
    is_assignee = current_user.user_id == incident.assigned_to_id
    is_irt_member = current_user.role in {
        models.UserRole.MIEMBRO_IRT,
        models.UserRole.LIDER_IRT,
        models.UserRole.ADMINISTRADOR,
    }

    if not (is_reporter or is_assignee or is_irt_member):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a este incidente.",
        )
    return incident


# --- Dependencias de Entidades de Usuario ---

def get_user_or_404(user_id: int, db: Session = Depends(get_db)) -> models.User:
    """
    Obtiene un usuario por su ID o devuelve un error 404 si no se encuentra.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado."
        )
    return user


def get_user_with_permission(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """
    Obtiene un usuario por ID y verifica el permiso de acceso.

    Permite el acceso si el usuario actual es el mismo que se solicita, o si es un administrador.
    """
    user = get_user_or_404(user_id, db)
    if not (current_user.user_id == user.user_id or current_user.role == UserRole.ADMINISTRADOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver o modificar este usuario.",
        )
    return user


# --- Dependencias de Entidades de Grupo ---

def get_group_or_404(group_id: int, db: Session = Depends(get_db)) -> models.Group:
    """
    Obtiene un grupo por su ID o devuelve un error 404 si no se encuentra.
    """
    group = crud.group.get(db, id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Grupo no encontrado."
        )
    return group
from incident_api.models import IncidentStatus


def validate_status_change_permission(user: models.User, incident: models.Incident, new_status: IncidentStatus):
    """
    Valida si un usuario tiene permiso para cambiar el estado de un incidente.
    """
    is_admin = user.role == UserRole.ADMINISTRADOR
    is_irt_leader = user.role == UserRole.LIDER_IRT
    is_irt_member = user.role == UserRole.MIEMBRO_IRT

    if incident.status == IncidentStatus.CERRADO and not (
        is_admin or is_irt_leader
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Un incidente cerrado solo puede ser modificado por un Administrador o Líder IRT.",
        )

    if new_status == IncidentStatus.CERRADO and not (is_admin or is_irt_leader):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un Administrador o Líder IRT puede cerrar un incidente.",
        )

    if not (is_admin or is_irt_leader or is_irt_member):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cambiar el estado de un incidente.",
        )


# --- Service Dependencies ---

from incident_api.services.audit_service import AuditService
from incident_api.services.incident_creation_service import IncidentCreationService

def get_audit_service() -> AuditService:
    """
    Dependency to get an instance of the AuditService.
    """
    return AuditService()

def get_incident_creation_service() -> IncidentCreationService:
    """
    Dependency to get an instance of the IncidentCreationService.
    """
    return IncidentCreationService()