"""
Pruebas de integración para los endpoints de gestión de clasificación de incidentes.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Dict

from incident_api import crud
from incident_api.core.config import settings
from incident_api.models import UserRole
from incident_api.schemas import UserCreate, AssetTypeCreate, AssetCreate, IncidentCategoryCreate, IncidentTypeCreate, AttackVectorCreate
from tests.utils.common import random_lower_string


def test_create_asset_type_by_admin(
    test_client: TestClient, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba la creación exitosa de un tipo de activo por un administrador."""
    # Crear tipo de activo
    asset_type_name = f"AssetType {random_lower_string(6)}"
    asset_type_in = AssetTypeCreate(name=asset_type_name, description="Test Asset Type Description")
    r = test_client.post(
        f"{settings.API_V1_STR}/classification/asset-types/", headers=admin_user_token_headers, json=asset_type_in.model_dump()
    )

    # Verificar
    assert r.status_code == 201
    created_asset_type = r.json()
    assert created_asset_type["name"] == asset_type_name
    assert created_asset_type["description"] == "Test Asset Type Description"
    assert "asset_type_id" in created_asset_type


def test_create_asset_type_by_non_admin(test_client: TestClient, db_session_override: Session) -> None:
    """Prueba que un usuario no-admin no puede crear un tipo de activo."""
    # Crear usuario normal y obtener token
    user_email = f"user_{random_lower_string(5)}@test.com"
    user_password = random_lower_string(12)
    user_in = UserCreate(email=user_email, password=user_password, full_name="Normal User", role=UserRole.EMPLEADO)
    crud.user.create(db_session_override, obj_in=user_in)
    login_data = {"username": user_email, "password": user_password}
    r = test_client.post(f"{settings.API_V1_STR}/login/token", data=login_data)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Intentar crear tipo de activo
    asset_type_in = AssetTypeCreate(name="Attempted Asset Type")
    r = test_client.post(f"{settings.API_V1_STR}/classification/asset-types/", headers=headers, json=asset_type_in.model_dump())

    # Verificar
    assert r.status_code == 403


def test_create_asset_by_admin(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba la creación exitosa de un activo por un administrador."""
    # Crear tipo de activo primero
    asset_type_in = AssetTypeCreate(name=f"AssetType {random_lower_string(6)}")
    asset_type = crud.asset_type.create(db_session_override, obj_in=asset_type_in)

    # Crear activo
    asset_name = f"Asset {random_lower_string(6)}"
    asset_in = AssetCreate(name=asset_name, asset_type_id=asset_type.asset_type_id, description="Test Asset Description")
    r = test_client.post(
        f"{settings.API_V1_STR}/classification/assets/", headers=admin_user_token_headers, json=asset_in.model_dump()
    )

    # Verificar
    assert r.status_code == 201
    created_asset = r.json()
    assert created_asset["name"] == asset_name
    assert created_asset["description"] == "Test Asset Description"
    assert created_asset["asset_type_id"] == asset_type.asset_type_id
    assert "asset_id" in created_asset


def test_create_asset_by_non_admin(test_client: TestClient, db_session_override: Session) -> None:
    """Prueba que un usuario no-admin no puede crear un activo."""
    # Crear usuario normal y obtener token
    user_email = f"user_{random_lower_string(5)}@test.com"
    user_password = random_lower_string(12)
    user_in = UserCreate(email=user_email, password=user_password, full_name="Normal User", role=UserRole.EMPLEADO)
    crud.user.create(db_session_override, obj_in=user_in)
    login_data = {"username": user_email, "password": user_password}
    r = test_client.post(f"{settings.API_V1_STR}/login/token", data=login_data)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Intentar crear activo
    asset_in = AssetCreate(name="Attempted Asset", asset_type_id=1)
    r = test_client.post(f"{settings.API_V1_STR}/classification/assets/", headers=headers, json=asset_in.model_dump())

    # Verificar
    assert r.status_code == 403


def test_create_incident_category_by_admin(
    test_client: TestClient, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba la creación exitosa de una categoría de incidente por un administrador."""
    # Crear categoría de incidente
    category_name = f"IncidentCategory {random_lower_string(6)}"
    category_in = IncidentCategoryCreate(name=category_name, description="Test Incident Category Description")
    r = test_client.post(
        f"{settings.API_V1_STR}/classification/incident-categories/", headers=admin_user_token_headers, json=category_in.model_dump()
    )

    # Verificar
    assert r.status_code == 201
    created_category = r.json()
    assert created_category["name"] == category_name
    assert created_category["description"] == "Test Incident Category Description"
    assert "incident_category_id" in created_category


def test_create_incident_category_by_non_admin(test_client: TestClient, db_session_override: Session) -> None:
    """Prueba que un usuario no-admin no puede crear una categoría de incidente."""
    # Crear usuario normal y obtener token
    user_email = f"user_{random_lower_string(5)}@test.com"
    user_password = random_lower_string(12)
    user_in = UserCreate(email=user_email, password=user_password, full_name="Normal User", role=UserRole.EMPLEADO)
    crud.user.create(db_session_override, obj_in=user_in)
    login_data = {"username": user_email, "password": user_password}
    r = test_client.post(f"{settings.API_V1_STR}/login/token", data=login_data)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Intentar crear categoría de incidente
    category_in = IncidentCategoryCreate(name="Attempted Incident Category")
    r = test_client.post(f"{settings.API_V1_STR}/classification/incident-categories/", headers=headers, json=category_in.model_dump())

    # Verificar
    assert r.status_code == 403


def test_create_incident_type_by_admin(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba la creación exitosa de un tipo de incidente por un administrador."""
    # Crear categoría de incidente primero
    category_in = IncidentCategoryCreate(name=f"IncidentCategory {random_lower_string(6)}")
    category = crud.incident_category.create(db_session_override, obj_in=category_in)

    # Crear tipo de incidente
    type_name = f"IncidentType {random_lower_string(6)}"
    type_in = IncidentTypeCreate(name=type_name, incident_category_id=category.incident_category_id, description="Test Incident Type Description")
    r = test_client.post(
        f"{settings.API_V1_STR}/classification/incident-types/", headers=admin_user_token_headers, json=type_in.model_dump()
    )

    # Verificar
    assert r.status_code == 201
    created_type = r.json()
    assert created_type["name"] == type_name
    assert created_type["description"] == "Test Incident Type Description"
    assert created_type["incident_category_id"] == category.incident_category_id
    assert "incident_type_id" in created_type


def test_create_incident_type_by_non_admin(test_client: TestClient, db_session_override: Session) -> None:
    """Prueba que un usuario no-admin no puede crear un tipo de incidente."""
    # Crear usuario normal y obtener token
    user_email = f"user_{random_lower_string(5)}@test.com"
    user_password = random_lower_string(12)
    user_in = UserCreate(email=user_email, password=user_password, full_name="Normal User", role=UserRole.EMPLEADO)
    crud.user.create(db_session_override, obj_in=user_in)
    login_data = {"username": user_email, "password": user_password}
    r = test_client.post(f"{settings.API_V1_STR}/login/token", data=login_data)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Intentar crear tipo de incidente
    type_in = IncidentTypeCreate(name="Attempted Incident Type", incident_category_id=1)
    r = test_client.post(f"{settings.API_V1_STR}/classification/incident-types/", headers=headers, json=type_in.model_dump())

    # Verificar
    assert r.status_code == 403


def test_create_attack_vector_by_admin(
    test_client: TestClient, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba la creación exitosa de un vector de ataque por un administrador."""
    # Crear vector de ataque
    vector_name = f"AttackVector {random_lower_string(6)}"
    vector_in = AttackVectorCreate(name=vector_name, description="Test Attack Vector Description")
    r = test_client.post(
        f"{settings.API_V1_STR}/classification/attack-vectors/", headers=admin_user_token_headers, json=vector_in.model_dump()
    )

    # Verificar
    assert r.status_code == 201
    created_vector = r.json()
    assert created_vector["name"] == vector_name
    assert created_vector["description"] == "Test Attack Vector Description"
    assert "attack_vector_id" in created_vector


def test_create_attack_vector_by_non_admin(test_client: TestClient, db_session_override: Session) -> None:
    """Prueba que un usuario no-admin no puede crear un vector de ataque."""
    # Crear usuario normal y obtener token
    user_email = f"user_{random_lower_string(5)}@test.com"
    user_password = random_lower_string(12)
    user_in = UserCreate(email=user_email, password=user_password, full_name="Normal User", role=UserRole.EMPLEADO)
    crud.user.create(db_session_override, obj_in=user_in)
    login_data = {"username": user_email, "password": user_password}
    r = test_client.post(f"{settings.API_V1_STR}/login/token", data=login_data)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Intentar crear vector de ataque
    vector_in = AttackVectorCreate(name="Attempted Attack Vector")
    r = test_client.post(f"{settings.API_V1_STR}/classification/attack-vectors/", headers=headers, json=vector_in.model_dump())

    # Verificar
    assert r.status_code == 403


def test_read_asset_types(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba que se pueden obtener todos los tipos de activo."""
    # Crear algunos tipos de activo
    asset_type_in_1 = AssetTypeCreate(name=f"AssetType {random_lower_string(6)}")
    crud.asset_type.create(db_session_override, obj_in=asset_type_in_1)
    asset_type_in_2 = AssetTypeCreate(name=f"AssetType {random_lower_string(6)}")
    crud.asset_type.create(db_session_override, obj_in=asset_type_in_2)

    # Obtener tipos de activo
    r = test_client.get(f"{settings.API_V1_STR}/classification/asset-types/", headers=admin_user_token_headers)

    # Verificar
    assert r.status_code == 200
    asset_types = r.json()
    assert isinstance(asset_types, list)
    assert len(asset_types) >= 2


def test_read_assets(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba que se pueden obtener todos los activos."""
    # Crear tipo de activo
    asset_type_in = AssetTypeCreate(name=f"AssetType {random_lower_string(6)}")
    asset_type = crud.asset_type.create(db_session_override, obj_in=asset_type_in)

    # Crear algunos activos
    asset_in_1 = AssetCreate(name=f"Asset {random_lower_string(6)}", asset_type_id=asset_type.asset_type_id)
    crud.asset.create(db_session_override, obj_in=asset_in_1)
    asset_in_2 = AssetCreate(name=f"Asset {random_lower_string(6)}", asset_type_id=asset_type.asset_type_id)
    crud.asset.create(db_session_override, obj_in=asset_in_2)

    # Obtener activos
    r = test_client.get(f"{settings.API_V1_STR}/classification/assets/", headers=admin_user_token_headers)

    # Verificar
    assert r.status_code == 200
    assets = r.json()
    assert isinstance(assets, list)
    assert len(assets) >= 2


def test_read_incident_categories(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba que se pueden obtener todas las categorías de incidente."""
    # Crear algunas categorías
    category_in_1 = IncidentCategoryCreate(name=f"IncidentCategory {random_lower_string(6)}")
    crud.incident_category.create(db_session_override, obj_in=category_in_1)
    category_in_2 = IncidentCategoryCreate(name=f"IncidentCategory {random_lower_string(6)}")
    crud.incident_category.create(db_session_override, obj_in=category_in_2)

    # Obtener categorías
    r = test_client.get(f"{settings.API_V1_STR}/classification/incident-categories/", headers=admin_user_token_headers)

    # Verificar
    assert r.status_code == 200
    categories = r.json()
    assert isinstance(categories, list)
    assert len(categories) >= 2


def test_read_incident_types(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba que se pueden obtener todos los tipos de incidente."""
    # Crear categoría
    category_in = IncidentCategoryCreate(name=f"IncidentCategory {random_lower_string(6)}")
    category = crud.incident_category.create(db_session_override, obj_in=category_in)

    # Crear algunos tipos
    type_in_1 = IncidentTypeCreate(name=f"IncidentType {random_lower_string(6)}", incident_category_id=category.incident_category_id)
    crud.incident_type.create(db_session_override, obj_in=type_in_1)
    type_in_2 = IncidentTypeCreate(name=f"IncidentType {random_lower_string(6)}", incident_category_id=category.incident_category_id)
    crud.incident_type.create(db_session_override, obj_in=type_in_2)

    # Obtener tipos
    r = test_client.get(f"{settings.API_V1_STR}/classification/incident-types/", headers=admin_user_token_headers)

    # Verificar
    assert r.status_code == 200
    types = r.json()
    assert isinstance(types, list)
    assert len(types) >= 2


def test_read_attack_vectors(
    test_client: TestClient, db_session_override: Session, admin_user_token_headers: Dict[str, str]
) -> None:
    """Prueba que se pueden obtener todos los vectores de ataque."""
    # Crear algunos vectores
    vector_in_1 = AttackVectorCreate(name=f"AttackVector {random_lower_string(6)}")
    crud.attack_vector.create(db_session_override, obj_in=vector_in_1)
    vector_in_2 = AttackVectorCreate(name=f"AttackVector {random_lower_string(6)}")
    crud.attack_vector.create(db_session_override, obj_in=vector_in_2)

    # Obtener vectores
    r = test_client.get(f"{settings.API_V1_STR}/classification/attack-vectors/", headers=admin_user_token_headers)

    # Verificar
    assert r.status_code == 200
    vectors = r.json()
    assert isinstance(vectors, list)
    assert len(vectors) >= 2