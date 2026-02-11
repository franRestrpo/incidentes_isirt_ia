"""
Pruebas de integración para los endpoints de gestión de incidentes.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from datetime import datetime

from incident_api import crud
from incident_api.core.config import settings
from incident_api.models import UserRole
from incident_api.schemas import UserCreate, IncidentCreate
from tests.utils.common import random_lower_string
from tests.utils.incident_category import create_random_incident_category
from tests.utils.incident_type import create_random_incident_type


def test_create_incident(
    test_client: TestClient, db_session_override: Session
) -> None:
    """
    Prueba la creación exitosa de un incidente por parte de un usuario empleado.
    """
    # 1. Crear un usuario para autenticarse
    user_email = f"user_{random_lower_string(5)}@test.com"
    user_password = random_lower_string(12)
    user_in = UserCreate(
        email=user_email,
        password=user_password,
        full_name="Test User",
        role=UserRole.EMPLEADO
    )
    crud.user.create(db_session_override, obj_in=user_in)

    # 2. Obtener su token de autenticación
    login_data = {"username": user_email, "password": user_password}
    r = test_client.post(f"{settings.API_V1_STR}/login/token", data=login_data)
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Crear las dependencias necesarias: categoría y tipo de incidente
    category = create_random_incident_category(db_session_override)
    inc_type = create_random_incident_type(db_session_override, category_id=category.incident_category_id)

    # 4. Preparar y enviar la petición para crear el incidente
    incident_summary = f"Incidente de prueba {random_lower_string(6)}"
    incident_description = "Descripción detallada del incidente de prueba."
    incident_data = IncidentCreate(
        summary=incident_summary,
        description=incident_description,
        discovery_time=datetime.now(),
        incident_type_id=inc_type.incident_type_id
    )

    r = test_client.post(
        f"{settings.API_V1_STR}/incidents/", 
        headers=headers, 
        data={"incident_data": incident_data.model_dump_json()}
    )

    # 5. Verificar el resultado
    assert r.status_code == 201
    created_incident = r.json()
    assert created_incident["summary"] == incident_summary
    assert created_incident["description"] == incident_description
    assert created_incident["status"] == "Nuevo" # Estado inicial por defecto
    assert created_incident["reporter"]["email"] == user_email
    assert created_incident["incident_type"]["incident_category"]["incident_category_id"] == category.incident_category_id
    assert created_incident["incident_type"]["incident_type_id"] == inc_type.incident_type_id


def test_get_all_incidents(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers
) -> None:
    """
    Prueba que un administrador puede obtener todos los incidentes.
    """
    # 1. Realizar la solicitud para obtener todos los incidentes
    r = test_client.get(f"{settings.API_V1_STR}/incidents/", headers=admin_user_token_headers)
    
    # 2. Verificar el resultado
    assert r.status_code == 200
    incidents = r.json()
    assert isinstance(incidents, list)

def test_get_incident_by_id(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers
) -> None:
    """
    Prueba que un usuario puede obtener un incidente por su ID.
    """
    # 1. Crear un incidente para obtener
    category = create_random_incident_category(db_session_override)
    inc_type = create_random_incident_type(db_session_override, category_id=category.incident_category_id)
    incident_in = IncidentCreate(
        summary="Test Incident",
        description="Test Description",
        discovery_time=datetime.now(),
        incident_type_id=inc_type.incident_type_id
    )
    incident = crud.incident.create(
        db=db_session_override, obj_in=incident_in, reported_by_id=1
    )
    
    # 2. Realizar la solicitud para obtener el incidente por ID
    r = test_client.get(f"{settings.API_V1_STR}/incidents/{incident.incident_id}", headers=admin_user_token_headers)
    
    # 3. Verificar el resultado
    assert r.status_code == 200
    retrieved_incident = r.json()
    assert retrieved_incident["incident_id"] == incident.incident_id
    assert retrieved_incident["summary"] == incident.summary

def test_update_incident(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers
) -> None:
    """
    Prueba que un administrador puede actualizar un incidente.
    """
    # 1. Crear un incidente para actualizar
    category = create_random_incident_category(db_session_override)
    inc_type = create_random_incident_type(db_session_override, category_id=category.incident_category_id)
    incident_in = IncidentCreate(
        summary="Test Incident",
        description="Test Description",
        discovery_time=datetime.now(),
        incident_type_id=inc_type.incident_type_id
    )
    incident = crud.incident.create(
        db=db_session_override, obj_in=incident_in, reported_by_id=1
    )
    
    # 2. Datos de actualización
    updated_data = {
        "summary": "Updated Summary",
        "description": "Updated Description",
        "status": "Investigando"
    }
    
    # 3. Realizar la solicitud de actualización
    r = test_client.put(f"{settings.API_V1_STR}/incidents/{incident.incident_id}", headers=admin_user_token_headers, json=updated_data)
    
    # 4. Verificar el resultado
    assert r.status_code == 200
    updated_incident = r.json()
    assert updated_incident["summary"] == "Updated Summary"
    assert updated_incident["description"] == "Updated Description"
    assert updated_incident["status"] == "Investigando"

def test_delete_incident(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers
) -> None:
    """
    Prueba que un administrador puede eliminar un incidente.
    """
    # 1. Crear un incidente para eliminar
    category = create_random_incident_category(db_session_override)
    inc_type = create_random_incident_type(db_session_override, category_id=category.incident_category_id)
    incident_in = IncidentCreate(
        summary="Test Incident",
        description="Test Description",
        discovery_time=datetime.now(),
        incident_type_id=inc_type.incident_type_id
    )
    incident_to_delete = crud.incident.create(
        db=db_session_override, obj_in=incident_in, reported_by_id=1
    )
    
    # 2. Realizar la solicitud de eliminación
    r = test_client.delete(f"{settings.API_V1_STR}/incidents/{incident_to_delete.incident_id}", headers=admin_user_token_headers)
    
    # 3. Verificar el resultado
    assert r.status_code == 200
    deleted_incident_data = r.json()
    assert deleted_incident_data["incident_id"] == incident_to_delete.incident_id
    
    # 4. Verificar que el incidente ya no existe en la base de datos
    deleted_incident_in_db = crud.incident.get(db_session_override, id=incident_to_delete.incident_id)
    assert deleted_incident_in_db is None