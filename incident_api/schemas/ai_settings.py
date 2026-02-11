"""
Esquemas de Pydantic para los modelos de configuración de IA.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any

# --- Esquemas para AIModelSettings ---


class AISettingsBase(BaseModel):
    """Esquema base para la configuración del modelo de IA."""

    model_provider: str = Field(
        default="gemini", description="Proveedor del modelo (e.g., 'gemini', 'openai')."
    )
    model_name: str = Field(
        default="gemini-1.5-pro-latest",
        description="Nombre del modelo específico a utilizar.",
    )
    system_prompt: str = Field(
        default="Eres un asistente experto en ciberseguridad...",
        description="Prompt del sistema para guiar el comportamiento del modelo.",
    )
    isirt_prompt: str = Field(
        default="Eres un asistente de IA experto en ciberseguridad para el equipo de respuesta a incidentes (ISIRT)...",
        description="Prompt del sistema para el chatbot del equipo ISIRT.",
    )
    parameters: Dict[str, Any] = Field(
        default_factory=lambda: {"temperature": 0.7},
        description="Parámetros de configuración para la inferencia del modelo.",
    )


class AISettingsCreate(AISettingsBase):
    """Esquema para crear la configuración de IA. Se espera una sola fila en la BD."""

    pass


class AISettingsUpdate(BaseModel):
    """Esquema para actualizar la configuración de IA. Todos los campos son opcionales."""

    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    system_prompt: Optional[str] = None
    isirt_prompt: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class AISettingsInDB(AISettingsBase):
    """Esquema para devolver la configuración de IA desde la API."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Esquemas para AvailableAIModel ---


class AvailableAIModelBase(BaseModel):
    """Esquema base para los modelos de IA disponibles."""

    provider: str = Field(..., description="Proveedor del modelo.")
    model_name: str = Field(..., description="Nombre del modelo disponible.")


class AvailableAIModelCreate(AvailableAIModelBase):
    """Esquema para registrar un nuevo modelo de IA disponible."""

    pass


class AvailableAIModelInDB(AvailableAIModelBase):
    """Esquema para devolver un modelo disponible desde la API."""

    id: int

    model_config = ConfigDict(from_attributes=True)
