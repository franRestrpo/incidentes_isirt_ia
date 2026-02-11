"""Utilidades y funciones de ayuda para la API."""
import os
import uuid
from fastapi import HTTPException, status

def secure_join(base: str, path: str) -> str:
    """
    Une de forma segura un directorio base y una ruta, previniendo path traversal.

    Args:
        base: El directorio base seguro.
        path: La ruta que se quiere unir.

    Returns:
        La ruta completa y segura.

    Raises:
        HTTPException: Si la ruta intenta escapar del directorio base.
    """
    # Normalizar la ruta para resolver '..' y otros patrones
    full_path = os.path.realpath(os.path.join(base, path))
    base_real = os.path.realpath(base)

    # Comprobar si la ruta final está dentro del directorio base
    if not full_path.startswith(base_real):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ruta de archivo no válida o maliciosa."
        )
    return full_path

def generate_safe_filename(filename: str) -> str:
    """
    Genera un nombre de archivo seguro para evitar colisiones y path traversal.

    Args:
        filename: El nombre de archivo original.

    Returns:
        Un nombre de archivo único y seguro.
    """
    # Extraer la extensión del archivo de forma segura
    extension = os.path.splitext(filename)[1]
    
    # Generar un nombre de archivo único usando UUID
    safe_filename = f"{uuid.uuid4()}{extension}"
    
    return safe_filename