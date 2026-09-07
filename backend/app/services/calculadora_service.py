# ============================================================
# Servicio de Calculadora (con logging)
# ============================================================
# Mismo servicio que V3, pero ahora registra cada operación.
# Esto nos permite:
# - Auditar qué operaciones se realizan
# - Detectar patrones de uso
# - Diagnosticar errores rápidamente
# ============================================================

from app.core.logger import logger


class CalculadoraService:
    """Servicio que contiene la lógica de las operaciones matemáticas."""

    @staticmethod
    def sumar(a: float, b: float) -> float:
        resultado = a + b
        logger.info(f"Operación: {a} + {b} = {resultado}")
        return resultado

    @staticmethod
    def restar(a: float, b: float) -> float:
        resultado = a - b
        logger.info(f"Operación: {a} - {b} = {resultado}")
        return resultado

    @staticmethod
    def multiplicar(a: float, b: float) -> float:
        resultado = a * b
        logger.info(f"Operación: {a} * {b} = {resultado}")
        return resultado

    @staticmethod
    def dividir(a: float, b: float) -> float:
        if b == 0:
            logger.warning(f"Intento de división entre cero: {a} / {b}")
            raise ValueError("No se puede dividir entre cero")
        resultado = a / b
        logger.info(f"Operación: {a} / {b} = {resultado}")
        return resultado
