"""
Pruebas de integración para los endpoints de gestión de grupos.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict

from incident_api import crud
from incident_api.core.config import settings
from incident_api.models import UserRole
from incident_api.schemas import UserCreate, GroupCreate
from tests.utils.common import random_lower_string


def test_create_group_by_admin(
    test_client: TestClient, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba la creación exitosa de un grupo por un administrador."""
    # Crear grupo
    group_name = f"Group {random_lower_string(6)}"
    group_in = GroupCreate(name=group_name, description="Test Group Description")
    r = test_client.post(
        f"{settings.API_V1_STR}/groups/", headers=admin_user_token_headers, json=group_in.model_dump()
    )

    # Verificar
    assert r.status_code == 201
    created_group = r.json()
    assert created_group["name"] == group_name
    assert created_group["description"] == "Test Group Description"
    assert "id" in created_group


def test_create_group_by_non_admin(test_client: TestClient, db_session_override: Session) -> None:
    """Prueba que un usuario no-admin no puede crear un grupo."""
    # Crear usuario normal y obtener token
    user_email = f"user_{random_lower_string(5)}@test.com"
    user_password = random_lower_string(12)
    user_in = UserCreate(email=user_email, password=user_password, full_name="Normal User", role=UserRole.EMPLEADO)
    crud.user.create(db_session_override, obj_in=user_in)
    login_data = {"username": user_email, "password": user_password}
    r = test_client.post(f"{settings.API_V1_STR}/login/token", data=login_data)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Intentar crear grupo
    group_in = GroupCreate(name="Attempted Group")
    r = test_client.post(f"{settings.API_V1_STR}/groups/", headers=headers, json=group_in.model_dump())

    # Verificar
    assert r.status_code == 403

def test_create_existing_group_name(
    test_client: TestClient, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba que no se puede crear un grupo con un nombre existente."""
    # Crear un primer grupo
    group_name = f"Unique Group {random_lower_string(6)}"
    group_in_1 = GroupCreate(name=group_name)
    r = test_client.post(
        f"{settings.API_V1_STR}/groups/", headers=admin_user_token_headers, json=group_in_1.model_dump()
    )
    assert r.status_code == 201

    # Intentar crear otro con el mismo nombre
    group_in_2 = GroupCreate(name=group_name)
    r = test_client.post(
        f"{settings.API_V1_STR}/groups/", headers=admin_user_token_headers, json=group_in_2.model_dump()
    )

    # Verificar
    assert r.status_code == 400
    assert "Ya existe un grupo con este nombre." in r.json()["detail"]

def test_get_all_groups(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba que un administrador puede obtener todos los grupos."""
    # 1. Crear algunos grupos para asegurarse de que la base de datos no está vacía
    group_in_1 = GroupCreate(name=f"Group {random_lower_string(6)}")
    crud.group.create(db_session_override, obj_in=group_in_1)
    group_in_2 = GroupCreate(name=f"Group {random_lower_string(6)}")
    crud.group.create(db_session_override, obj_in=group_in_2)

    # 2. Realizar la solicitud para obtener todos los grupos
    r = test_client.get(f"{settings.API_V1_STR}/groups/", headers=admin_user_token_headers)
    
    # 3. Verificar el resultado
    assert r.status_code == 200
    groups = r.json()
    assert isinstance(groups, list)
    assert len(groups) >= 2

def test_get_group_by_id(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba que un administrador puede obtener un grupo por su ID."""
    # 1. Crear un grupo para obtener
    group_in = GroupCreate(name=f"Group {random_lower_string(6)}")
    group = crud.group.create(db_session_override, obj_in=group_in)
    
    # 2. Realizar la solicitud para obtener el grupo por ID
    r = test_client.get(f"{settings.API_V1_STR}/groups/{group.id}", headers=admin_user_token_headers)
    
    # 3. Verificar el resultado
    assert r.status_code == 200
    retrieved_group = r.json()
    assert retrieved_group["id"] == group.id
    assert retrieved_group["name"] == group.name

def test_update_group(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba que un administrador puede actualizar un grupo."""
    # 1. Crear un grupo para actualizar
    group_in = GroupCreate(name=f"Group {random_lower_string(6)}")
    group = crud.group.create(db_session_override, obj_in=group_in)
    
    # 2. Datos de actualización
    updated_data = {
        "name": f"Updated Group {random_lower_string(6)}",
        "description": "Updated Description"
    }
    
    # 3. Realizar la solicitud de actualización
    r = test_client.put(f"{settings.API_V1_STR}/groups/{group.id}", headers=admin_user_token_headers, json=updated_data)
    
    # 4. Verificar el resultado
    assert r.status_code == 200
    updated_group = r.json()
    assert updated_group["name"] == updated_data["name"]
    assert updated_group["description"] == "Updated Description"

def test_delete_group(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba que un administrador puede eliminar un grupo."""
    # 1. Crear un grupo para eliminar
    group_in = GroupCreate(name=f"Group {random_lower_string(6)}")
    group_to_delete = crud.group.create(db_session_override, obj_in=group_in)
    
    # 2. Realizar la solicitud de eliminación
    r = test_client.delete(f"{settings.API_V1_STR}/groups/{group_to_delete.id}", headers=admin_user_token_headers)
    
    # 3. Verificar el resultado
    assert r.status_code == 200
    deleted_group_data = r.json()
    assert deleted_group_data["id"] == group_to_delete.id
    
    # 4. Verificar que el grupo ya no existe en la base de datos
    deleted_group_in_db = crud.group.get(db_session_override, id=group_to_delete.id)
    assert deleted_group_in_db is None