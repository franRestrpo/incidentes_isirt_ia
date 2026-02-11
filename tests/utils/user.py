"""
Utilidades para la gestión de usuarios en las pruebas.
"""

from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from incident_api import crud, schemas
from incident_api.core.config import settings
from incident_api.models import User, UserRole
from tests.utils.common import random_email, random_lower_string


def create_random_user(
    db: Session, role: UserRole = UserRole.EMPLEADO, group_id: int | None = None
) -> User:
    """
    Crea un usuario con datos aleatorios directamente en la base de datos.

    Args:
        db (Session): Sesión de la base de datos de prueba.
        role (UserRole): Rol del usuario a crear.
        group_id (int, optional): ID del grupo al que pertenecerá. Defaults to None.

    Returns:
        User: El objeto del usuario creado.
    """
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email,
        password=password,
        full_name=random_lower_string(),
        role=role,
        group_id=group_id,
    )
    return crud.user.create(db, obj_in=user_in)


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> Dict[str, str]:
    """
    Se autentica con un email y contraseña de un usuario existente y devuelve el header de autorización.

    Args:
        client (TestClient): Cliente de prueba de FastAPI.
        email (str): Email del usuario.
        db (Session): Sesión de la base de datos.

    Returns:
        Dict[str, str]: Header de autorización con el token Bearer.
    """
    # La contraseña es la misma que el email en los datos de prueba iniciales
    # o la que se haya generado aleatoriamente. Para simplificar, asumimos que
    # la contraseña de prueba es conocida. Para este caso, la contraseña es "password"
    # según el `seed_data`. Si usamos `create_random_user`, la contraseña no la conocemos.
    # Vamos a necesitar una forma de obtenerla o fijarla.

    # Solución: Para las pruebas, vamos a fijar la contraseña.
    password = "testpassword"
    user = crud.user.get_by_email(db, email=email)
    if user:
        # Actualizamos la contraseña del usuario a una conocida para la prueba
        user_in_update = schemas.UserUpdate(password=password)
        crud.user.update(db, db_obj=user, obj_in=user_in_update)
    else:
        # Si el usuario no existe, lo creamos con la contraseña conocida
        user_in_create = schemas.UserCreate(
            email=email,
            password=password,
            full_name=random_lower_string(),
            role=UserRole.USUARIO,
        )
        crud.user.create(db, obj_in=user_in_create)

    data = {"username": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers
