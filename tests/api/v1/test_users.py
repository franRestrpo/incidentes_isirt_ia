"""
Pruebas de integración para los endpoints de gestión de usuarios.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict
import json
import csv
import io
import xml.etree.ElementTree as ET

from incident_api import crud
from incident_api.core.config import settings
from incident_api.models import UserRole
from incident_api.schemas import UserCreate
from tests.utils.common import random_email, random_lower_string
from tests.utils.user import create_random_user


def test_create_user_by_admin(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """
    Prueba la creación exitosa de un usuario por parte de un administrador.
    """
    # 1. Usar el token de admin para crear un nuevo usuario normal
    new_user_email = random_email()
    new_user_password = random_lower_string()
    new_user_data = {
        "email": new_user_email,
        "password": new_user_password,
        "full_name": "Normal User",
        "role": "Empleado",
        "is_active": True
    }
    r = test_client.post(f"{settings.API_V1_STR}/users/", headers=admin_user_token_headers, json=new_user_data)
    
    # 2. Verificar el resultado
    assert r.status_code == 201
    created_user = r.json()
    assert created_user["email"] == new_user_email
    assert created_user["full_name"] == "Normal User"
    assert "user_id" in created_user

    # 3. Verificar que el usuario existe en la base de datos
    db_user = crud.user.get_by_email(db_session_override, email=new_user_email)
    assert db_user is not None
    assert db_user.email == new_user_email


def test_create_user_by_non_admin(
    test_client: TestClient, db_session_override: Session
) -> None:
    """
    Prueba que un usuario no administrador no puede crear otros usuarios.
    """
    # 1. Crear un usuario normal en la BD para autenticarse
    user_email = random_email()
    user_password = random_lower_string()
    user_in = UserCreate(
        email=user_email,
        password=user_password,
        full_name="Normal User",
        role=UserRole.EMPLEADO
    )
    crud.user.create(db_session_override, obj_in=user_in)

    login_data = {"username": user_email, "password": user_password}
    r = test_client.post(f"{settings.API_V1_STR}/login/token", data=login_data)
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Intentar crear un nuevo usuario con el token del usuario normal
    new_user_data = {
        "email": random_email(),
        "password": random_lower_string(),
        "full_name": "Another User",
        "role": "Empleado"
    }
    r = test_client.post(f"{settings.API_V1_STR}/users/", headers=headers, json=new_user_data)

    # 3. Verificar que la operación es denegada
    assert r.status_code == 403  # Forbidden


def test_create_user_existing_email(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """
    Prueba que no se puede crear un usuario con un email que ya existe.
    """
    # 1. Crear un primer usuario
    user_email = random_email()
    user_password = random_lower_string()
    user_data = {
        "email": user_email,
        "password": user_password,
        "full_name": "Test User",
        "role": "Empleado",
    }
    r = test_client.post(f"{settings.API_V1_STR}/users/", headers=admin_user_token_headers, json=user_data)
    assert r.status_code == 201

    # 2. Intentar crear otro usuario con el mismo email
    another_user_data = {
        "email": user_email,  # Mismo email
        "password": random_lower_string(),
        "full_name": "Another User",
        "role": "Empleado",
    }
    r = test_client.post(f"{settings.API_V1_STR}/users/", headers=admin_user_token_headers, json=another_user_data)

    # 3. Verificar que la API devuelve un error 400
    assert r.status_code == 400
    assert "Un usuario con este correo electrónico ya existe." in r.json()["detail"]


def test_get_all_users(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """
    Prueba que un administrador puede obtener todos los usuarios.
    """
    # 1. Crear algunos usuarios para asegurarse de que la base de datos no está vacía
    create_random_user(db_session_override)
    create_random_user(db_session_override)

    # 2. Realizar la solicitud para obtener todos los usuarios
    r = test_client.get(f"{settings.API_V1_STR}/users/", headers=admin_user_token_headers)
    
    # 3. Verificar el resultado
    assert r.status_code == 200
    users = r.json()
    assert isinstance(users, list)
    assert len(users) >= 2  # Debería haber al menos los usuarios que creamos

def test_get_user_by_id(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """
    Prueba que un administrador puede obtener un usuario por su ID.
    """
    # 1. Crear un usuario para obtener
    user = create_random_user(db_session_override)
    
    # 2. Realizar la solicitud para obtener el usuario por ID
    r = test_client.get(f"{settings.API_V1_STR}/users/{user.user_id}", headers=admin_user_token_headers)
    
    # 3. Verificar el resultado
    assert r.status_code == 200
    retrieved_user = r.json()
    assert retrieved_user["user_id"] == user.user_id
    assert retrieved_user["email"] == user.email

def test_update_user(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """
    Prueba que un administrador puede actualizar un usuario.
    """
    # 1. Crear un usuario para actualizar
    user = create_random_user(db_session_override)
    
    # 2. Datos de actualización
    updated_data = {
        "full_name": "Updated Name",
        "email": random_email(),
        "role": "Líder IRT",
        "is_active": False
    }
    
    # 3. Realizar la solicitud de actualización
    r = test_client.put(f"{settings.API_V1_STR}/users/{user.user_id}", headers=admin_user_token_headers, json=updated_data)
    
    # 4. Verificar el resultado
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["full_name"] == "Updated Name"
    assert updated_user["email"] == updated_data["email"]
    assert updated_user["role"] == "Líder IRT"
    assert not updated_user["is_active"]

def test_delete_user(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """
    Prueba que un administrador puede eliminar un usuario.
    """
    # 1. Crear un usuario para eliminar
    user_to_delete = create_random_user(db_session_override)
    
    # 2. Realizar la solicitud de eliminación
    r = test_client.delete(f"{settings.API_V1_STR}/users/{user_to_delete.user_id}", headers=admin_user_token_headers)
    
    # 3. Verificar el resultado
    assert r.status_code == 200
    deleted_user_data = r.json()
    assert deleted_user_data["user_id"] == user_to_delete.user_id
    
    # 4. Verificar que el usuario ya no existe en la base de datos
    deleted_user_in_db = crud.user.get(db_session_override, id=user_to_delete.user_id)
    assert deleted_user_in_db is None


def test_export_users_json(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """
    Prueba la exportación de usuarios en formato JSON.
    """
    # 1. Crear algunos usuarios
    user1 = create_random_user(db_session_override)
    user2 = create_random_user(db_session_override)

    # 2. Realizar la solicitud de exportación en JSON
    r = test_client.get(f"{settings.API_V1_STR}/users/export?format=json", headers=admin_user_token_headers)

    # 3. Verificar el resultado
    if r.status_code != 200:
        print(f"Error: {r.status_code} - {r.text}")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/json"
    assert "attachment; filename=users.json" in r.headers["content-disposition"]

    # 4. Parsear el JSON y verificar integridad de datos
    exported_users = json.loads(r.content.decode())
    assert isinstance(exported_users, list)
    assert len(exported_users) >= 2  # Al menos los usuarios creados

    # Verificar que los datos coincidan con la BD
    user_ids = [u["user_id"] for u in exported_users]
    assert user1.user_id in user_ids
    assert user2.user_id in user_ids

    # Verificar que no se exportan datos sensibles
    for user in exported_users:
        assert "hashed_password" not in user


def test_export_users_csv(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """
    Prueba la exportación de usuarios en formato CSV.
    """
    # 1. Crear algunos usuarios
    user1 = create_random_user(db_session_override)
    user2 = create_random_user(db_session_override)

    # 2. Realizar la solicitud de exportación en CSV
    r = test_client.get(f"{settings.API_V1_STR}/users/export?format=csv", headers=admin_user_token_headers)

    # 3. Verificar el resultado
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "attachment; filename=users.csv" in r.headers["content-disposition"]

    # 4. Parsear el CSV y verificar integridad de datos
    csv_content = r.content.decode()
    csv_reader = csv.DictReader(io.StringIO(csv_content))
    exported_users = list(csv_reader)
    assert len(exported_users) >= 2

    # Verificar que los datos coincidan con la BD
    user_ids = [int(u["user_id"]) for u in exported_users]
    assert user1.user_id in user_ids
    assert user2.user_id in user_ids


def test_export_users_xml(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """
    Prueba la exportación de usuarios en formato XML.
    """
    # 1. Crear algunos usuarios
    user1 = create_random_user(db_session_override)
    user2 = create_random_user(db_session_override)

    # 2. Realizar la solicitud de exportación en XML
    r = test_client.get(f"{settings.API_V1_STR}/users/export?format=xml", headers=admin_user_token_headers)

    # 3. Verificar el resultado
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/xml"
    assert "attachment; filename=users.xml" in r.headers["content-disposition"]

    # 4. Parsear el XML y verificar integridad de datos
    xml_content = r.content.decode()
    root = ET.fromstring(xml_content)
    exported_users = root.findall("user")
    assert len(exported_users) >= 2

    # Verificar que los datos coincidan con la BD
    user_ids = [int(u.find("user_id").text) for u in exported_users]
    assert user1.user_id in user_ids
    assert user2.user_id in user_ids


def test_export_users_with_filters(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """
    Prueba la exportación de usuarios con filtros de estado y rol.
    """
    # 1. Crear usuarios con diferentes estados y roles
    active_user = create_random_user(db_session_override, role=UserRole.EMPLEADO)
    inactive_user = create_random_user(db_session_override, role=UserRole.ADMINISTRADOR)
    # Desactivar uno de los usuarios
    crud.user.deactivate(db_session_override, db_obj=inactive_user)

    # 2. Exportar solo usuarios activos
    r = test_client.get(f"{settings.API_V1_STR}/users/export?format=json&status=active", headers=admin_user_token_headers)
    assert r.status_code == 200
    exported_users = json.loads(r.content.decode())
    user_ids = [u["user_id"] for u in exported_users]
    assert active_user.user_id in user_ids
    assert inactive_user.user_id not in user_ids

    # 3. Exportar solo usuarios inactivos
    r = test_client.get(f"{settings.API_V1_STR}/users/export?format=json&status=inactive", headers=admin_user_token_headers)
    assert r.status_code == 200
    exported_users = json.loads(r.content.decode())
    user_ids = [u["user_id"] for u in exported_users]
    assert inactive_user.user_id in user_ids
    assert active_user.user_id not in user_ids

    # 4. Exportar por rol
    r = test_client.get(f"{settings.API_V1_STR}/users/export?format=json&role=Administrador", headers=admin_user_token_headers)
    assert r.status_code == 200
    exported_users = json.loads(r.content.decode())
    user_ids = [u["user_id"] for u in exported_users]
    assert inactive_user.user_id in user_ids
    assert active_user.user_id not in user_ids


def test_export_users_permissions(
    test_client: TestClient, db_session_override: Session
) -> None:
    """
    Prueba que solo administradores pueden exportar usuarios.
    """
    # 1. Crear un usuario normal
    user_email = random_email()
    user_password = random_lower_string()
    user_in = UserCreate(
        email=user_email,
        password=user_password,
        full_name="Normal User",
        role=UserRole.EMPLEADO
    )
    crud.user.create(db_session_override, obj_in=user_in)

    # 2. Autenticar como usuario normal
    login_data = {"username": user_email, "password": user_password}
    r = test_client.post(f"{settings.API_V1_STR}/login/token", data=login_data)
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Intentar exportar con usuario normal
    r = test_client.get(f"{settings.API_V1_STR}/users/export", headers=headers)
    assert r.status_code == 403  # Forbidden


def test_export_users_invalid_format_defaults_to_json(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """
    Prueba que un formato inválido por defecto exporta en JSON.
    """
    # 1. Realizar la solicitud con formato inválido
    r = test_client.get(f"{settings.API_V1_STR}/users/export?format=invalid", headers=admin_user_token_headers)

    # 2. Verificar que se comporta como JSON
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/json"
    assert "attachment; filename=users.json" in r.headers["content-disposition"]

    # 3. Verificar que el contenido es JSON válido
    exported_users = json.loads(r.content.decode())
    assert isinstance(exported_users, list)


def test_export_users_content_negotiation(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """
    Prueba la selección de formato mediante content negotiation (Accept header).
    """
    # 1. Crear algunos usuarios
    user1 = create_random_user(db_session_override)
    user2 = create_random_user(db_session_override)

    # 2. Probar JSON via Accept header
    headers_json = admin_user_token_headers.copy()
    headers_json["Accept"] = "application/json"
    r = test_client.get(f"{settings.API_V1_STR}/users/export", headers=headers_json)
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/json"
    exported_users = json.loads(r.content.decode())
    assert isinstance(exported_users, list)
    assert len(exported_users) >= 2

    # 3. Probar CSV via Accept header
    headers_csv = admin_user_token_headers.copy()
    headers_csv["Accept"] = "text/csv"
    r = test_client.get(f"{settings.API_V1_STR}/users/export", headers=headers_csv)
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    csv_content = r.content.decode()
    csv_reader = csv.DictReader(io.StringIO(csv_content))
    exported_users_csv = list(csv_reader)
    assert len(exported_users_csv) >= 2

    # 4. Probar XML via Accept header
    headers_xml = admin_user_token_headers.copy()
    headers_xml["Accept"] = "application/xml"
    r = test_client.get(f"{settings.API_V1_STR}/users/export", headers=headers_xml)
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/xml"
    xml_content = r.content.decode()
    root = ET.fromstring(xml_content)
    exported_users_xml = root.findall("user")
    assert len(exported_users_xml) >= 2

    # 5. Verificar que el parámetro format tiene prioridad sobre Accept header
    headers_mixed = admin_user_token_headers.copy()
    headers_mixed["Accept"] = "application/xml"  # Accept dice XML
    r = test_client.get(f"{settings.API_V1_STR}/users/export?format=json", headers=headers_mixed)  # Pero format dice JSON
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/json"  # Debe ser JSON
