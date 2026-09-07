from pydantic import BaseModel


class OperacionRequest(BaseModel):
    """Modelo de entrada para las operaciones de la calculadora."""
    a: float
    b: float


class OperacionResponse(BaseModel):
    """Modelo de respuesta estándar para las operaciones."""
    operacion: str
    a: float
    b: float
    resultado: float


class HealthResponse(BaseModel):
    """Modelo de respuesta para el health check."""
    status: str
    version: str


class ErrorResponse(BaseModel):
    """Modelo de respuesta para errores."""
    detail: str
