# ============================================================
# Middleware de Logging
# ============================================================
# Intercepta TODAS las peticiones que entran y salen.
# Registra: método, ruta, status code y tiempo de respuesta.
#
# Un middleware es como una "capa envolvente" que se ejecuta
# antes y después de cada endpoint, sin modificar el código
# de los endpoints.
# ============================================================

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware que registra cada petición HTTP."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # --- Antes del endpoint ---
        start_time = time.time()
        method = request.method
        path = request.url.path

        logger.info(
            f"→ {method} {path}",
        )

        # --- Ejecutar el endpoint ---
        try:
            response = await call_next(request)
        except Exception as exc:
            # Si hay una excepción no manejada, la logueamos
            duration = time.time() - start_time
            logger.error(
                f"✗ {method} {path} - Error no manejado en {duration:.3f}s: {exc}",
                exc_info=True,
            )
            raise

        # --- Después del endpoint ---
        duration = time.time() - start_time
        status_code = response.status_code

        # Elegir nivel de log según el status code
        if status_code >= 500:
            logger.error(f"← {method} {path} - {status_code} en {duration:.3f}s")
        elif status_code >= 400:
            logger.warning(f"← {method} {path} - {status_code} en {duration:.3f}s")
        else:
            logger.info(f"← {method} {path} - {status_code} en {duration:.3f}s")

        return response
