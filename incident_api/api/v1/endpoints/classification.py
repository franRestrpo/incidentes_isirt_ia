"""
Endpoints de la API para la gestión de la clasificación de incidentes.

Este módulo contiene los endpoints para gestionar los activos, las categorías,
los tipos y los vectores de ataque.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from incident_api import crud, schemas, models
from incident_api.api import dependencies
from incident_api.services import (
    asset_type_service,
    asset_service,
    incident_category_service,
    incident_type_service,
    attack_vector_service,
)

router = APIRouter()


@router.get("/asset-types/", response_model=List[schemas.AssetTypeInDB])
def read_asset_types(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Recupera una lista paginada de todos los tipos de activos disponibles en el sistema.
    
    Args:
        db (Session): Dependencia de la sesión de la base de datos.
        skip (int): Número de registros a omitir.
        limit (int): Número máximo de registros a devolver.
        
    Returns:
        List[schemas.AssetTypeInDB]: Una lista de tipos de activos.
    """
    asset_types = crud.asset_type.get_multi(db, skip=skip, limit=limit)
    return asset_types


@router.post("/asset-types/", response_model=schemas.AssetTypeInDB, status_code=status.HTTP_201_CREATED)
def create_asset_type(
    asset_type_in: schemas.AssetTypeCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Crea un nuevo tipo de activo en el sistema.
    
    Este endpoint está restringido a usuarios con el rol de **Administrador**.
    
    Args:
        asset_type_in (schemas.AssetTypeCreate): Los datos del nuevo tipo de activo.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): El usuario administrador que realiza la operación.
        
    Returns:
        schemas.AssetTypeInDB: El tipo de activo recién creado.
    """
    return asset_type_service.create_asset_type(db=db, asset_type_in=asset_type_in)


@router.get("/assets/", response_model=List[schemas.AssetInDB])
def read_assets(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    asset_type_id: Optional[int] = None,
):
    """
    Recupera una lista de activos, opcionalmente filtrada por tipo de activo.
    
    Este endpoint es útil para poblar menús desplegables en cascada en el frontend.
    
    Args:
        db (Session): Dependencia de la sesión de la base de datos.
        skip (int): Número de registros a omitir.
        limit (int): Número máximo de registros a devolver.
        asset_type_id (Optional[int]): El ID del tipo de activo para filtrar los resultados.
        
    Returns:
        List[schemas.AssetInDB]: Una lista de activos.
    """
    assets = asset_service.get_assets(db, skip=skip, limit=limit, asset_type_id=asset_type_id)
    return assets


@router.post("/assets/", response_model=schemas.AssetInDB, status_code=status.HTTP_201_CREATED)
def create_asset(
    asset_in: schemas.AssetCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Crea un nuevo activo en el sistema.
    
    Este endpoint está restringido a usuarios con el rol de **Administrador**.
    
    Args:
        asset_in (schemas.AssetCreate): Los datos del nuevo activo.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): El usuario administrador que realiza la operación.
        
    Returns:
        schemas.AssetInDB: El activo recién creado.
    """
    return asset_service.create_asset(db=db, asset_in=asset_in)


@router.get("/incident-categories/", response_model=List[schemas.IncidentCategoryInDB])
def read_incident_categories(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Recupera una lista paginada de todas las categorías de incidentes.
    
    Args:
        db (Session): Dependencia de la sesión de la base de datos.
        skip (int): Número de registros a omitir.
        limit (int): Número máximo de registros a devolver.
        
    Returns:
        List[schemas.IncidentCategoryInDB]: Una lista de categorías de incidentes.
    """
    incident_categories = crud.incident_category.get_multi(db, skip=skip, limit=limit)
    return incident_categories


@router.post("/incident-categories/", response_model=schemas.IncidentCategoryInDB, status_code=status.HTTP_201_CREATED)
def create_incident_category(
    incident_category_in: schemas.IncidentCategoryCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Crea una nueva categoría de incidente.
    
    Este endpoint está restringido a usuarios con el rol de **Administrador**.
    
    Args:
        incident_category_in (schemas.IncidentCategoryCreate): Los datos de la nueva categoría.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): El usuario administrador que realiza la operación.
        
    Returns:
        schemas.IncidentCategoryInDB: La categoría de incidente recién creada.
    """
    return incident_category_service.create_incident_category(db=db, incident_category_in=incident_category_in)


@router.get("/incident-types/", response_model=List[schemas.IncidentTypeInDB])
def read_incident_types(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    incident_category_id: Optional[int] = None,
):
    """
    Recupera una lista de tipos de incidente, opcionalmente filtrada por categoría.
    
    Este endpoint es útil para poblar menús desplegables en cascada en el frontend.
    
    Args:
        db (Session): Dependencia de la sesión de la base de datos.
        skip (int): Número de registros a omitir.
        limit (int): Número máximo de registros a devolver.
        incident_category_id (Optional[int]): El ID de la categoría para filtrar los resultados.
        
    Returns:
        List[schemas.IncidentTypeInDB]: Una lista de tipos de incidente.
    """
    incident_types = incident_type_service.get_incident_types(db, skip=skip, limit=limit, incident_category_id=incident_category_id)
    return incident_types


@router.post("/incident-types/", response_model=schemas.IncidentTypeInDB, status_code=status.HTTP_201_CREATED)
def create_incident_type(
    incident_type_in: schemas.IncidentTypeCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Crea un nuevo tipo de incidente.
    
    Este endpoint está restringido a usuarios con el rol de **Administrador**.
    
    Args:
        incident_type_in (schemas.IncidentTypeCreate): Los datos del nuevo tipo de incidente.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): El usuario administrador que realiza la operación.
        
    Returns:
        schemas.IncidentTypeInDB: El tipo de incidente recién creado.
    """
    return incident_type_service.create_incident_type(db=db, incident_type_in=incident_type_in)


@router.get("/attack-vectors/", response_model=List[schemas.AttackVectorInDB])
def read_attack_vectors(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Recupera una lista paginada de todos los vectores de ataque disponibles.
    
    Args:
        db (Session): Dependencia de la sesión de la base de datos.
        skip (int): Número de registros a omitir.
        limit (int): Número máximo de registros a devolver.
        
    Returns:
        List[schemas.AttackVectorInDB]: Una lista de vectores de ataque.
    """
    attack_vectors = crud.attack_vector.get_multi(db, skip=skip, limit=limit)
    return attack_vectors


@router.post("/attack-vectors/", response_model=schemas.AttackVectorInDB, status_code=status.HTTP_201_CREATED)
def create_attack_vector(
    attack_vector_in: schemas.AttackVectorCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin_user),
):
    """
    Crea un nuevo vector de ataque.
    
    Este endpoint está restringido a usuarios con el rol de **Administrador**.
    
    Args:
        attack_vector_in (schemas.AttackVectorCreate): Los datos del nuevo vector de ataque.
        db (Session): Dependencia de la sesión de la base de datos.
        current_user (models.User): El usuario administrador que realiza la operación.
        
    Returns:
        schemas.AttackVectorInDB: El vector de ataque recién creado.
    """
    return attack_vector_service.create_attack_vector(db=db, attack_vector_in=attack_vector_in)
