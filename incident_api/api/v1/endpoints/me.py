"""
Endpoints de la API para la gestión del perfil del usuario autenticado.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from incident_api import schemas, models
from incident_api.api import dependencies
from incident_api.services import user_service

router = APIRouter()


@router.get("/", response_model=schemas.UserInDB, summary="Obtener mi perfil")
def read_current_user(
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    Obtiene los detalles del usuario actualmente autenticado.
    """
    return current_user


@router.put("/", response_model=schemas.UserInDB, summary="Actualizar mi perfil")
def update_current_user(
    user_update: schemas.UserUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    Actualiza la información del perfil del usuario actualmente autenticado.

    Un usuario no puede cambiar su propio rol o grupo a través de este endpoint.
    """
    updated_user = user_service.update_user(db, user=current_user, user_in=user_update, current_user=current_user)
    return updated_user


@router.post(
    "/deactivate", response_model=schemas.UserInDB, summary="Desactivar mi cuenta"
)
def deactivate_current_user(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    Desactiva la cuenta del usuario actualmente autenticado.
    """
    deactivated_user = user_service.deactivate_user(db, current_user.user_id)
    if deactivated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado."
        )
    return deactivated_user
