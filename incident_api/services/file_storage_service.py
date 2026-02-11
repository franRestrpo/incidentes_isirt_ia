"""
Servicio para el manejo de almacenamiento de archivos.
"""

import os
import shutil
import uuid
import hashlib
from typing import List
from fastapi import HTTPException, status, UploadFile

from incident_api.core.config import settings
import logging

UPLOADS_DIR = "uploads"
logger = logging.getLogger(__name__)


class FileStorageService:
    """
    Servicio para manejar el almacenamiento de archivos de evidencia.
    """

    def save_evidence_files(
        self, incident_id: int, files: List[UploadFile]
    ) -> List[dict]:
        """
        Guarda múltiples archivos de evidencia, calcula su hash y devuelve la información.

        Returns:
            Lista de diccionarios con info de cada archivo:
            {'file_path', 'file_name', 'file_type', 'file_size', 'file_hash'}
        """
        logger.debug(f"Iniciando guardado de {len(files)} archivo(s) para incidente {incident_id}")

        os.makedirs(UPLOADS_DIR, exist_ok=True)
        allowed_types = set(settings.ALLOWED_FILE_MIME_TYPES.split(','))
        max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024

        saved_files = []

        for file in files:
            logger.debug(f"Procesando archivo: {file.filename}, Tipo: {file.content_type}")

            # Validar tipo de archivo
            if file.content_type not in allowed_types:
                logger.warning(f"Tipo de archivo no permitido: {file.content_type} para {file.filename}")
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    f"El tipo de archivo para '{file.filename}' no es válido.",
                )

            # Generar nombre seguro
            _, extension = os.path.splitext(file.filename)
            extension = extension.lower()
            safe_filename = f"{uuid.uuid4()}{extension}"
            file_location = os.path.join(UPLOADS_DIR, f"{incident_id}_{safe_filename}")

            sha256_hash = hashlib.sha256()
            file_size = 0

            try:
                with open(file_location, "wb") as file_object:
                    while chunk := file.file.read(4096): # Leer en chunks de 4KB
                        if file_size + len(chunk) > max_size_bytes:
                            os.remove(file_location) # Eliminar archivo parcial
                            logger.warning(f"Archivo demasiado grande: {file.filename}")
                            raise HTTPException(
                                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                                f"El archivo '{file.filename}' excede el tamaño máximo de {settings.MAX_FILE_SIZE_MB} MB.",
                            )
                        file_object.write(chunk)
                        sha256_hash.update(chunk)
                        file_size += len(chunk)

                file_hex_hash = sha256_hash.hexdigest()
                logger.info(f"Archivo guardado: {file.filename} -> {file_location}, Hash: {file_hex_hash}")

                saved_files.append({
                    'file_path': file_location,
                    'file_name': file.filename,
                    'file_type': file.content_type,
                    'file_size': file_size,
                    'file_hash': file_hex_hash
                })

            except Exception as e:
                logger.error(f"Error al guardar archivo {file.filename}: {str(e)}", exc_info=True)
                # Asegurarse de que el archivo parcial se elimine si hay un error
                if os.path.exists(file_location):
                    os.remove(file_location)
                raise
            finally:
                file.file.close()

        return saved_files


file_storage_service = FileStorageService()