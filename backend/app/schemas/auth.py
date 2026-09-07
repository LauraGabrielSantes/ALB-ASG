# ============================================================
# Schemas de autenticación
# ============================================================

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Respuesta del endpoint de login."""
    access_token: str
    token_type: str = "bearer"
