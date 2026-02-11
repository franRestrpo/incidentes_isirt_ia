"""
Endpoints para la gestión y servicio de archivos de evidencia de forma segura.
"""
import os
import mimetypes
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from incident_api import models
from incident_api.api import dependencies
from incident_api.core.utils import secure_join

router = APIRouter()

@router.get("/secure-uploads/{file_path:path}", tags=["Files"])
async def serve_secure_file(file_path: str, current_user: models.User = Depends(dependencies.get_current_active_user)):
    """
    Sirve archivos de evidencia de manera segura, validando la autenticación.
    Muestra archivos seguros (imágenes, PDF) en línea y fuerza la descarga para otros tipos.

    TODO: Añadir lógica de autorización para verificar si el usuario tiene permiso
    para ver la evidencia de este incidente específico.
    """
    # La ruta del archivo es relativa a la raíz del proyecto (ej. 'uploads/file.jpeg')
    project_root = os.path.abspath(".") # Esto es /app dentro del contenedor
    full_path = secure_join(project_root, file_path)

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado en la ruta: {full_path}")

    # Determinar el tipo MIME del archivo
    mime_type, _ = mimetypes.guess_type(full_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    # Lista de tipos MIME seguros para mostrar en línea
    safe_inline_types = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
        "application/pdf"
    ]

    headers = {}
    if mime_type in safe_inline_types:
        headers["Content-Disposition"] = "inline"
    else:
        headers["Content-Disposition"] = "attachment"

    return FileResponse(full_path, media_type=mime_type, headers=headers)
