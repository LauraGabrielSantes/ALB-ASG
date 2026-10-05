# ============================================================
# Router de Health Check
# ============================================================

from fastapi import APIRouter, HTTPException
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

@router.get("/boom", summary="Endpoint de prueba que devuelve 500")
def boom():
    """Endpoint intencionalmente roto para la demostración de rollback."""
    raise HTTPException(status_code=500, detail="boom")
