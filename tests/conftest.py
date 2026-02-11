"""
Archivo de configuración de Pytest para definir fixtures de prueba.
"""

import pytest
from typing import Generator, Dict

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from incident_api.main import app
from incident_api.api import dependencies
from incident_api.db.base import Base
from incident_api import crud
from incident_api.schemas import UserCreate
from incident_api.models import UserRole
from incident_api.core.config import settings
from tests.utils.common import random_lower_string

# URL de la base de datos de prueba (SQLite en memoria)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Crear un motor de base de datos específico para las pruebas
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Crear una sesión de prueba
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Fixture para crear y destruir la base de datos de prueba una vez por sesión.
    """
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    yield
    # Destruir todas las tablas
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session_override() -> Generator[Session, None, None]:
    """
    Fixture para sobreescribir la dependencia get_db y usar la base de datos de prueba.
    """
    connection = engine.connect()
    trans = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    trans.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session_override: Session) -> Generator[TestClient, None, None]:
    """
    Fixture que proporciona un cliente de prueba para la API.
    """

    def override_get_db():
        try:
            yield db_session_override
        finally:
            pass

    app.dependency_overrides[dependencies.get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    # Limpiar la sobreescritura después de la prueba
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_user_token_headers(test_client: TestClient, db_session_override: Session) -> Dict[str, str]:
    """
    Crea un usuario administrador y devuelve sus headers de autenticación.
    """
    admin_email = f"admin_{random_lower_string(5)}@test.com"
    admin_password = random_lower_string(12)
    user_in = UserCreate(
        email=admin_email,
        password=admin_password,
        full_name="Test Admin User",
        role=UserRole.ADMINISTRADOR
    )
    crud.user.create(db_session_override, obj_in=user_in)

    login_data = {"username": admin_email, "password": admin_password}
    r = test_client.post(f"{settings.API_V1_STR}/login/token", data=login_data)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers