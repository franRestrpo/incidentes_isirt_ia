"""
Configuración de logging para la aplicación.
"""
import os
import logging
from logging.config import dictConfig

from incident_api.core.config import settings

# Determinar el nivel de log basado en el modo DEBUG
LOG_LEVEL = "DEBUG" if settings.DEBUG else "INFO"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - [%(module)s:%(funcName)s:%(lineno)d] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": os.path.join(settings.LOGS_DIR, "incident_api.log"),
            "maxBytes": 10485760,
            "backupCount": 10,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "incident_api": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {"level": "INFO", "propagate": False},
        "uvicorn.access": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["console", "file"],
    },
}


def setup_logging():
    """Aplica la configuración de logging tras asegurar que el directorio exista."""
    log_dir = settings.LOGS_DIR
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        dictConfig(LOGGING_CONFIG)
    except (OSError, ValueError) as e:
        # Si hay problemas con el handler de archivo, usar solo consola
        print(f"Warning: Could not configure file logging: {e}. Using console logging only.")
        console_only_config = LOGGING_CONFIG.copy()
        console_only_config["handlers"] = {
            "console": LOGGING_CONFIG["handlers"]["console"]
        }
        console_only_config["loggers"]["incident_api"]["handlers"] = ["console"]
        console_only_config["loggers"]["uvicorn"]["handlers"] = ["console"]
        console_only_config["loggers"]["uvicorn.access"]["handlers"] = ["console"]
        console_only_config["root"]["handlers"] = ["console"]
        dictConfig(console_only_config)