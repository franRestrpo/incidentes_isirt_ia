"""
Esquemas de Pydantic para la configuración de RAG.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class RAGSettingsBase(BaseModel):
    """Esquema base para la configuración de RAG."""
    chunk_size: int = Field(
        default=1000, description="Tamaño de los trozos para el procesamiento RAG."
    )
    chunk_overlap: int = Field(
        default=150, description="Solapamiento de los trozos para el procesamiento RAG."
    )

class RAGSettingsCreate(RAGSettingsBase):
    """Esquema para crear la configuración de RAG."""
    pass

class RAGSettingsUpdate(BaseModel):
    """Esquema para actualizar la configuración de RAG."""
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None

class RAGSettingsInDB(RAGSettingsBase):
    """Esquema para devolver la configuración de RAG desde la API."""
    id: int
    model_config = ConfigDict(from_attributes=True)
