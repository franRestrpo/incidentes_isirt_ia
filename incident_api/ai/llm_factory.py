"""
Factory para la creación centralizada de instancias de modelos de lenguaje (LLM).

Este módulo abstrae la selección del proveedor de IA (Google, OpenAI, Ollama)
y devuelve un objeto compatible con la interfaz de LangChain ChatModel.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel

from incident_api.core.config import settings


def get_llm(provider: str, model_name: str, parameters: dict = None) -> BaseChatModel:
    """
    Obtiene una instancia de un modelo de chat de LangChain basado en el proveedor.

    Args:
        provider (str): El nombre del proveedor de IA (ej. "google", "openai", "ollama").
        model_name (str): El nombre específico del modelo a utilizar.
        parameters (dict, optional): Parámetros adicionales para el modelo (ej. temperature, top_p).

    Returns:
        BaseChatModel: Una instancia de un modelo de chat compatible con LangChain.

    Raises:
        ValueError: Si el proveedor no es soportado o si la clave de API/URL base requerida no está configurada.
    """
    if parameters is None:
        parameters = {}

    provider_lower = provider.lower()
    if provider_lower == "google" or provider_lower == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValueError("La clave de API de Gemini (GEMINI_API_KEY) no está configurada.")
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=parameters.get('temperature', 0.7),
            top_p=parameters.get('top_p', 1.0)
        )

    elif provider_lower == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("La clave de API de OpenAI (OPENAI_API_KEY) no está configurada.")
        return ChatOpenAI(
            model=model_name,
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=parameters.get('temperature', 0.7),
            top_p=parameters.get('top_p', 1.0)
        )

    elif provider_lower == "ollama":
        if not settings.OLLAMA_API_BASE_URL:
            raise ValueError("La URL base de Ollama (OLLAMA_API_BASE_URL) no está configurada.")
        return ChatOllama(
            base_url=settings.OLLAMA_API_BASE_URL,
            model=model_name,
            temperature=parameters.get('temperature', 0.7),
            top_p=parameters.get('top_p', 1.0)
        )

    elif provider_lower == "groq":
        if not settings.GROQ_API_KEY:
            raise ValueError("La clave de API de Groq (GROQ_API_KEY) no está configurada.")
        return ChatGroq(
            model_name=model_name,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=parameters.get('temperature', 0.7),
            top_p=parameters.get('top_p', 1.0)
        )

    else:
        raise ValueError(f"Proveedor de IA no soportado: '{provider}'")
