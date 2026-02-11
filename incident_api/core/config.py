"""Configuración de la aplicación FastAPI y variables de entorno."""
from pydantic import Field
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Settings(BaseSettings):
    """
    Clase de configuración para la aplicación FastAPI.

    Carga variables de entorno desde el archivo .env.
    """

    PROJECT_NAME: str = "API de Gestión de Incidentes de Seguridad"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = (
        "API para gestionar el ciclo de vida de los incidentes de seguridad, conforme a ISO 27001 y NIST."
    )
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = Field(
        default=False, description="Activa el modo de depuración."
    )
    ENVIRONMENT: str = Field(
        default="production",
        description="Entorno de ejecución (development o production)."
    )

    # Configuración específica de login por entorno
    LOGIN_MAX_ATTEMPTS: int = Field(
        default=5, description="Número máximo de intentos de login permitidos."
    )
    LOGIN_LOCKOUT_MINUTES: int = Field(
        default=15, description="Minutos de bloqueo tras exceder intentos máximos."
    )
    LOGIN_RATE_LIMIT_REQUESTS: int = Field(
        default=10, description="Número máximo de requests de login por ventana de tiempo."
    )
    LOGIN_RATE_LIMIT_WINDOW_MINUTES: int = Field(
        default=5, description="Ventana de tiempo en minutos para rate limiting."
    )

    CORS_ORIGINS: str = Field(
        default="",
        description="Orígenes permitidos para CORS (separados por comas). Debe configurarse en el archivo .env para evitar configuraciones inseguras.",
    )

    SECRET_KEY: str = Field(
        ..., description="Clave secreta para la firma de tokens JWT."
    )
    ALGORITHM: str = Field("HS256", description="Algoritmo de cifrado para JWT.")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        30, description="Tiempo de expiración de los tokens de acceso en minutos."
    )

    DATABASE_URL: str = Field(
        ...,
        description="URL de conexión a la base de datos PostgreSQL.",
    )

    # Directorio de logs
    LOGS_DIR: str = "/app/logs"

    # Políticas de carga de archivos
    ALLOWED_FILE_MIME_TYPES: str = Field(
        default="image/jpeg,image/png,application/pdf",
        env="ALLOWED_FILE_MIME_TYPES",
        description="Tipos MIME de archivo permitidos para carga (separados por comas).",
    )
    MAX_FILE_SIZE_MB: int = Field(
        default=5,
        env="MAX_FILE_SIZE_MB",
        description="Tamaño máximo de archivo para carga en MB.",
    )

    # Primer superusuario (para inicialización)
    FIRST_SUPERUSER_EMAIL: str = Field(
        ...,
        env="FIRST_SUPERUSER_EMAIL",
        description="Correo electrónico del primer superusuario.",
    )
    FIRST_SUPERUSER_PASSWORD: str = Field(
        ...,
        env="FIRST_SUPERUSER_PASSWORD",
        description="Contraseña del primer superusuario.",
    )
    FIRST_SUPERUSER_FULL_NAME: str = Field(
        default="Super Usuario",
        env="FIRST_SUPERUSER_FULL_NAME",
        description="Nombre completo del primer superusuario.",
    )

    # Claves de API de proveedores de IA
    OPENAI_API_KEY: Optional[str] = Field(
        None, env="OPENAI_API_KEY", description="Clave API para OpenAI."
    )
    GEMINI_API_KEY: Optional[str] = Field(
        None, env="GEMINI_API_KEY", description="Clave API para Google Gemini."
    )
    GROQ_API_KEY: Optional[str] = Field(
        None, env="GROQ_API_KEY", description="Clave API para Groq."
    )

    # Frontend URL
    FRONTEND_URL: str = Field(
        default="http://localhost:8081",
        env="FRONTEND_URL",
        description="URL base de la aplicación frontend.",
    )

    # Google OAuth2
    GOOGLE_CLIENT_ID: Optional[str] = Field(
        None, env="GOOGLE_CLIENT_ID", description="Google Client ID for OAuth2."
    )
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(
        None, env="GOOGLE_CLIENT_SECRET", description="Google Client Secret for OAuth2."
    )
    GOOGLE_REDIRECT_URI: Optional[str] = Field(
        None,
        env="GOOGLE_REDIRECT_URI",
        description="Google Redirect URI for OAuth2.",
    )

    # URL base de la API de Ollama (opcional)
    OLLAMA_API_BASE_URL: Optional[str] = Field(
        default="http://localhost:11434",
        env="OLLAMA_API_BASE_URL",
        description="URL base para la API de Ollama.",
    )

    class Config:
        """Configuración de Pydantic para la clase Settings."""
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
