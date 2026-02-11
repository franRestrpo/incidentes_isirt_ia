"""
Servicio para la generación de alertas de seguridad.

Este módulo centraliza la lógica para disparar alertas basadas en eventos críticos
del sistema, registrándolas en un archivo dedicado para monitoreo.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from functools import lru_cache

from incident_api.core.config import settings

# Usar lru_cache para asegurar que la configuración del logger se ejecute solo una vez
@lru_cache(maxsize=None)
def get_alert_logger():
    """Configura y devuelve un logger para alertas de seguridad."""
    LOG_DIR = settings.LOGS_DIR
    ALERT_LOG_FILE = os.path.join(LOG_DIR, "security_alerts.log")

    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("security_alerts")
    logger.setLevel(logging.WARNING)
    logger.propagate = False

    if not logger.handlers:
        handler = RotatingFileHandler(ALERT_LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

class AlertingService:
    """
    Servicio para disparar y registrar alertas de seguridad.
    """

    def trigger_alert(self, message: str, level: str = "warning") -> None:
        """
        Registra una alerta en el log de seguridad dedicado.

        Args:
            message (str): El mensaje de la alerta a registrar.
            level (str): El nivel de severidad de la alerta ('warning', 'error', 'critical').
        """
        alert_logger = get_alert_logger()
        log_level = getattr(logging, level.upper(), logging.WARNING)
        alert_logger.log(log_level, message)


# Instancia única del servicio para ser usada en la aplicación
alerting_service = AlertingService()
