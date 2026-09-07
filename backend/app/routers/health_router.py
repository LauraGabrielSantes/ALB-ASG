# ============================================================
# Router de Health Check
# ============================================================

from fastapi import APIRouter
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificar estado del servicio",
)
def health():
    """Retorna el estado actual del servicio."""
    return HealthResponse(status="ok", version="2.0.0")
