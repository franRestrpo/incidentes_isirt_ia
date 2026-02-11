"""
Esquemas de Pydantic para el modelo EvidenceFile.

Define los esquemas para la validación y serialización de los metadatos
de los archivos de evidencia en la API.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from .user import UserInDB  # Importar el esquema de usuario para anidarlo

# --- Esquemas para EvidenceFile ---


class EvidenceFileBase(BaseModel):
    """Esquema base para los archivos de evidencia."""

    file_name: str = Field(..., max_length=255, description="Nombre del archivo.")
    file_type: str = Field(..., max_length=100, description="Tipo MIME del archivo.")
    file_size_bytes: int = Field(..., gt=0, description="Tamaño del archivo en bytes.")
    file_hash: Optional[str] = None


class EvidenceFileCreate(EvidenceFileBase):
    """Esquema para la creación de un archivo de evidencia. El path se genera en el backend."""
    file_hash: str


class EvidenceFileInDB(EvidenceFileBase):
    """Esquema para devolver la información de un archivo desde la API."""

    file_id: int = Field(..., description="ID único del archivo.")
    incident_id: int = Field(..., description="ID del incidente asociado.")
    file_path: str = Field(..., description="Ruta de acceso al archivo.")
    uploaded_at: datetime = Field(..., description="Fecha y hora de subida.")
    uploader: UserInDB = Field(..., description="Usuario que subió el archivo.")

    model_config = ConfigDict(from_attributes=True)
