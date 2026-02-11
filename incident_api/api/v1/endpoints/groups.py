from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from typing import List

from incident_api import schemas, models, crud
from incident_api.api import dependencies
from incident_api.api.decorators import audit_action
from incident_api.services.group_service import GroupService

router = APIRouter()


@router.get(
    "/", response_model=List[schemas.GroupInDB], summary="Obtener todos los grupos"
)
def read_groups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(dependencies.get_db),
    admin_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Obtiene una lista de todos los grupos.

    Requiere privilegios de **Administrador**.

    Args:
        skip (int): Número de grupos a omitir para paginación.
        limit (int): Número máximo de grupos a devolver.
        db (Session): Dependencia de la sesión de la base de datos.
        admin_user (models.User): Dependencia que valida rol de Administrador.

    Returns:
        List[schemas.GroupInDB]: Una lista de objetos de grupo.
    """
    group_service = GroupService()
    groups = group_service.get_all_groups(db, skip=skip, limit=limit)
    return groups


@router.get(
    "/{group_id}", response_model=schemas.GroupInDB, summary="Obtener grupo por ID"
)
def read_group(
    group: models.Group = Depends(dependencies.get_group_or_404),
    admin_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Obtiene los detalles de un grupo específico por su ID.

    Requiere privilegios de **Administrador**.

    Args:
        group (models.Group): Dependencia que obtiene el grupo o devuelve 404.
        admin_user (models.User): Dependencia que valida rol de Administrador.

    Returns:
        schemas.GroupInDB: El objeto del grupo con sus detalles.
    """
    return group


@router.post(
    "/",
    response_model=schemas.GroupInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo grupo",
)
@audit_action(action="CREATE_GROUP", resource_type="GROUP")
def create_group(
    group_in: schemas.GroupCreate,
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Crea un nuevo grupo en el sistema.

    Requiere privilegios de **Administrador**.
    La validación de nombre único se maneja en la capa CRUD.
    Esta acción es auditada.

    Args:
        group_in (schemas.GroupCreate): Datos del nuevo grupo.
        request (Request): El objeto de la petición HTTP para la auditoría.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): Dependencia que valida rol de Administrador.

    Returns:
        schemas.GroupInDB: El grupo recién creado.
    """
    group_service = GroupService()
    new_group = group_service.create_group(db=db, group_in=group_in)
    return new_group


@router.put("/{group_id}", response_model=schemas.GroupInDB, summary="Actualizar grupo")
@audit_action(action="UPDATE_GROUP", resource_type="GROUP", resource_id_param="group_id", get_resource_func=crud.group.get)
def update_group(
    group_id: int,
    request: Request,
    group_update: schemas.GroupUpdate,
    group: models.Group = Depends(dependencies.get_group_or_404),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Actualiza la información de un grupo existente.

    Requiere privilegios de **Administrador**.
    Esta acción es auditada con detalle de cambios.

    Args:
        group_id (int): ID del grupo a actualizar.
        request (Request): El objeto de la petición HTTP para la auditoría.
        group_update (schemas.GroupUpdate): Campos a actualizar.
        group (models.Group): Dependencia que obtiene el grupo o devuelve 404.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): Dependencia que valida rol de Administrador.

    Returns:
        schemas.GroupInDB: El grupo actualizado.
    """
    group_service = GroupService()
    updated_group = group_service.update_group(
        db, group=group, group_in=group_update
    )
    return updated_group


@router.delete(
    "/{group_id}", response_model=schemas.GroupInDB, summary="Eliminar grupo"
)
@audit_action(action="DELETE_GROUP", resource_type="GROUP", resource_id_param="group_id", get_resource_func=crud.group.get)
def delete_group(
    group_id: int,
    request: Request,
    group: models.Group = Depends(dependencies.get_group_or_404),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Elimina un grupo del sistema.

    Requiere privilegios de **Administrador**.
    Esta acción es auditada.

    Args:
        group_id (int): ID del grupo a eliminar.
        request (Request): El objeto de la petición HTTP para la auditoría.
        group (models.Group): Dependencia que obtiene el grupo o devuelve 404.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): Dependencia que valida rol de Administrador.
    """
    group_service = GroupService()
    deleted_group = group_service.delete_group(db, group_id=group.id)
    return deleted_group