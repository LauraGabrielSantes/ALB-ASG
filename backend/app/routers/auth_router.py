# ============================================================
# Router de Autenticación
# ============================================================
# Endpoint de login que valida credenciales y retorna un JWT.
# En producción las credenciales se validan contra una BD
# y las contraseñas se almacenan hasheadas con bcrypt.
# ============================================================

from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

from app.core.config import settings
from app.core.security import crear_token_acceso
from app.schemas import TokenResponse

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión y obtener token",
)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Autentica al usuario y retorna un token JWT.

    **Credenciales de demo:**
    - Usuario: `admin`
    - Contraseña: `admin123`

    El token se envía en peticiones posteriores como:
    `Authorization: Bearer <token>`
    """
    # En producción: buscar usuario en BD y comparar hash
    if (
        form_data.username != settings.DEMO_USERNAME
        or form_data.password != settings.DEMO_PASSWORD
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token con el username como subject
    access_token = crear_token_acceso(data={"sub": form_data.username})

    return TokenResponse(access_token=access_token)
