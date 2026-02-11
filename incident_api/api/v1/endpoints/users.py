"""
Endpoints de la API para la gestión de usuarios.
"""

from typing import List, Literal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from incident_api import crud, models, schemas
from incident_api.api import dependencies
from incident_api.api.decorators import audit_action
from incident_api.services.user_service import UserService

router = APIRouter()


@router.get(
    "/", response_model=List[schemas.UserInDB], summary="Obtener todos los usuarios"
)
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(dependencies.get_db),
    admin_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Obtiene una lista de todos los usuarios registrados en el sistema.

    Requiere que el usuario actual sea un **Administrador**.

    Args:
        skip (int): Número de usuarios a omitir para paginación.
        limit (int): Número máximo de usuarios a devolver.
        db (Session): Dependencia de la sesión de la base de datos.
        admin_user (models.User): Dependencia que valida rol de Administrador.

    Returns:
        List[schemas.UserInDB]: Una lista de objetos de usuario.
    """
    user_service = UserService()
    users = user_service.get_all_users(db, skip=skip, limit=limit)
    return users


@router.post(
    "/", response_model=schemas.UserInDB, status_code=status.HTTP_201_CREATED, summary="Crear nuevo usuario"
)
@audit_action(action="CREATE_USER", resource_type="USER")
def create_user(
    user_in: schemas.UserCreate,
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Crea un nuevo usuario en el sistema.

    Requiere que el usuario actual sea un **Administrador**.
    La validación de email único se maneja en la capa CRUD.
    Esta acción es auditada.

    Args:
        user_in (schemas.UserCreate): Datos del nuevo usuario.
        request (Request): El objeto de la petición HTTP para la auditoría.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): Dependencia que valida rol de Administrador.

    Returns:
        schemas.UserInDB: El usuario recién creado.
    """
    user_service = UserService()
    new_user = user_service.create_user(db, user_in=user_in)
    return new_user


@router.get(
    "/irt-members",
    response_model=List[schemas.UserInDB],
    summary="Obtener miembros del IRT",
)
def get_irt_members(
    db: Session = Depends(dependencies.get_db),
    irt_user: models.User = Depends(dependencies.get_current_irt_user),
):
    """
    Obtiene una lista de todos los usuarios que son miembros o líderes del IRT.

    Requiere que el usuario actual sea un **Miembro IRT**, **Líder IRT** o **Administrador**.

    Args:
        db (Session): Dependencia de la sesión de la base de datos.
        irt_user (models.User): Dependencia que valida rol de IRT.

    Returns:
        List[schemas.UserInDB]: Lista de usuarios que pertenecen al IRT.
    """
    user_service = UserService()
    users = user_service.get_irt_members(db)
    return users


@router.get(
    "/export",
    summary="Exportar usuarios a CSV, JSON o XML",
)
def export_users(
    request: Request,
    format: str = None,
    status: str = None,
    role: str = None,
    db: Session = Depends(dependencies.get_db),
    admin_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Exporta una lista de todos los usuarios a un archivo CSV, JSON o XML.

    El formato se determina por:
    1. Parámetro 'format' en la query string ('json', 'csv', 'xml')
    2. Header 'Accept' para content negotiation:
       - application/json -> JSON
       - text/csv -> CSV
       - application/xml -> XML

    Requiere que el usuario actual sea un **Administrador**.

    Args:
        request (Request): La solicitud HTTP para acceder a headers.
        format (str, optional): El formato del archivo de exportación.
        status (str): Filtra los usuarios por estado ('active' o 'inactive').
        role (str): Filtra los usuarios por rol.
        db (Session): Dependencia de la sesión de la base de datos.

    Returns:
        StreamingResponse: Un archivo para descargar.
    """
    # Determinar el formato basado en content negotiation o parámetro
    if format:
        export_format = format.lower()
    else:
        accept_header = request.headers.get("accept", "")
        if "application/json" in accept_header:
            export_format = "json"
        elif "text/csv" in accept_header:
            export_format = "csv"
        elif "application/xml" in accept_header:
            export_format = "xml"
        else:
            export_format = "json"  # default

    print(f"Exporting users with filters: format={export_format}, status={status}, role={role}")

    return user_service.export_users(db, format=export_format, status=status, role=role)


@router.get(
    "/{user_id}", response_model=schemas.UserInDB, summary="Obtener usuario por ID"
)
def read_user(
    user: models.User = Depends(dependencies.get_user_with_permission),
):
    """
    Obtiene los detalles de un usuario específico por su ID.

    Requiere que el usuario actual sea un **Administrador** o el **mismo usuario** solicitado.

    Args:
        user (models.User): Dependencia que obtiene el usuario y valida permisos de lectura.

    Returns:
        schemas.UserInDB: El objeto del usuario con sus detalles.
    """
    return user


@router.put("/{user_id}", response_model=schemas.UserInDB, summary="Actualizar usuario")
@audit_action(action="UPDATE_USER", resource_type="USER", resource_id_param="user_id", get_resource_func=crud.user.get)
def update_user(
    user_id: int,
    request: Request,
    user_update: schemas.UserUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
    user_to_update: models.User = Depends(dependencies.get_user_with_permission),
):
    """
    Actualiza la información de un usuario existente.

    - Requiere que el usuario actual sea un **Administrador** o el **mismo usuario**.
    - Solo un **Administrador** puede cambiar el rol o el grupo de un usuario.
    - Esta acción es auditada con detalle de cambios.

    Args:
        user_id (int): ID del usuario a actualizar.
        request (Request): El objeto de la petición HTTP para la auditoría.
        user_update (schemas.UserUpdate): Campos a actualizar.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): El usuario que realiza la operación.
        user_to_update (models.User): Dependencia que obtiene el usuario a actualizar y valida permisos.

    Returns:
        schemas.UserInDB: El usuario actualizado.
    """
    user_service = UserService()
    updated_user = user_service.update_user(db, user=user_to_update, user_in=user_update, current_user=current_user)
    return updated_user


@router.delete(
    "/{user_id}", response_model=schemas.UserInDB, summary="Eliminar usuario"
)
@audit_action(action="DELETE_USER", resource_type="USER", resource_id_param="user_id", get_resource_func=crud.user.get)
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Elimina un usuario del sistema.

    Requiere que el usuario actual sea un **Administrador**.
    Esta acción es auditada con detalle de cambios.

    Args:
        user_id (int): ID del usuario a eliminar.
        request (Request): El objeto de la petición HTTP para la auditoría.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): Dependencia que valida rol de Administrador.

    Returns:
        schemas.UserInDB: El usuario que fue eliminado.
    """
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propia cuenta.",
        )
    user_service = UserService()
    db_user = user_service.delete_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado."
        )
    return db_user


@router.post(
    "/{user_id}/deactivate",
    response_model=schemas.UserInDB,
    summary="Desactivar usuario",
)
@audit_action(action="DEACTIVATE_USER", resource_type="USER", resource_id_param="user_id", get_resource_func=crud.user.get)
def deactivate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Desactiva la cuenta de un usuario, impidiendo su acceso al sistema.

    Requiere que el usuario actual sea un **Administrador**.
    Esta acción es auditada con detalle de cambios.

    Args:
        user_id (int): ID del usuario a desactivar.
        request (Request): El objeto de la petición HTTP para la auditoría.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): Dependencia que valida rol de Administrador.

    Returns:
        schemas.UserInDB: El usuario desactivado.
    """
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta.",
        )
    user_service = UserService()
    db_user = user_service.deactivate_user(db, user_id, performed_by=current_user)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado."
        )
    return db_user


@router.post(
    "/{user_id}/activate",
    response_model=schemas.UserInDB,
    summary="Activar usuario",
)
@audit_action(action="ACTIVATE_USER", resource_type="USER", resource_id_param="user_id", get_resource_func=crud.user.get)
def activate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Activa la cuenta de un usuario previamente desactivado.

    Requiere que el usuario actual sea un **Administrador**.
    Esta acción es auditada con detalle de cambios.

    Args:
        user_id (int): ID del usuario a activar.
        request (Request): El objeto de la petición HTTP para la auditoría.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): Dependencia que valida rol de Administrador.

    Returns:
        schemas.UserInDB: El usuario activado.
    """
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes activar tu propia cuenta de esta manera.",
        )
    user_service = UserService()
    db_user = user_service.activate_user(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado."
        )
    return db_user
