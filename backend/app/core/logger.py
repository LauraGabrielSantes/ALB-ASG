# ============================================================
# Configuración de Logging
# ============================================================
# Logging estructurado para producción.
#
# ¿Por qué NO usar print()?
# - print() no tiene niveles (INFO, WARNING, ERROR)
# - print() no incluye timestamp ni contexto
# - print() no se puede redirigir fácilmente a archivos o servicios
# - print() no se puede filtrar por severidad
#
# Usamos el módulo estándar de Python con formato JSON
# para que sea fácil integrarlo con herramientas como
# ELK Stack, Loki, o cualquier sistema de monitoreo.
# ============================================================

import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """
    Formateador que produce logs en formato JSON.
    Esto facilita la integración con herramientas de
    observabilidad (Grafana Loki, ELK, CloudWatch, etc).
    """

    def format(self, record: logging.LogRecord) -> str:
        import json

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Agregar información extra si existe
        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data

        # Agregar traceback si hay excepción
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logger(name: str = "calculadora-api") -> logging.Logger:
    """
    Configura y retorna un logger con formato JSON.

    Args:
        name: Nombre del logger

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Evitar duplicar handlers si se llama más de una vez
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    return logger


# Logger global de la aplicación
logger = setup_logger()
