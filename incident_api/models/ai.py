"""
Modelos de la base de datos para la configuración de IA.
"""

from sqlalchemy import Column, Integer, String, JSON
from incident_api.db.base import Base


class AIModelSettings(Base):
    """
    Modelo para almacenar la configuración del modelo de IA.
    Se espera que solo haya una fila en esta tabla, que contendrá la configuración activa.
    """

    __tablename__ = "ai_model_settings"

    id = Column(Integer, primary_key=True, index=True)
    model_provider = Column(String, default="gemini", nullable=False)
    model_name = Column(String, default="gemini-1.5-pro-latest", nullable=False)
    system_prompt = Column(
        String,
        default="Eres un asistente experto en ciberseguridad. Tu tarea es ayudar a los usuarios a describir y entender incidentes de seguridad de manera clara y concisa.",
        nullable=False,
    )
    isirt_prompt = Column(
        String,
        default="Eres un asistente de IA experto en ciberseguridad para el equipo de respuesta a incidentes (ISIRT). Basa tus respuestas únicamente en el contexto de los playbooks proporcionados.",
        nullable=False,
    )
    parameters = Column(JSON, default=lambda: {"temperature": 0.7, "top_p": 1.0})


class AvailableAIModel(Base):
    """
    Modelo para almacenar los nombres de los modelos de IA disponibles.
    """

    __tablename__ = "available_ai_models"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False, index=True)  # 'gemini' o 'openai'
    model_name = Column(String, nullable=False, unique=True)


class RAGSettings(Base):
    """
    Modelo para almacenar la configuración del pre-procesamiento RAG.
    Se espera que solo haya una fila en esta tabla con la configuración activa.
    """

    __tablename__ = "rag_settings"

    id = Column(Integer, primary_key=True, index=True)
    chunk_size = Column(Integer, default=1000, nullable=False)
    chunk_overlap = Column(Integer, default=150, nullable=False)
