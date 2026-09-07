# ============================================================
# Seguridad: Manejo de tokens JWT
# ============================================================
# Este módulo se encarga de:
# - Crear tokens de acceso (access token)
# - Validar tokens en cada petición protegida
# - Extraer la información del usuario desde el token
#
# Usamos python-jose para JWT y passlib para hashing
# de contraseñas (aunque en esta demo no hasheamos).
# ============================================================

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings

# --- Esquema OAuth2 ---
# Esto le dice a FastAPI que los endpoints protegidos
# esperan un token en el header: Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def crear_token_acceso(data: dict) -> str:
    """
    Crea un JWT con los datos proporcionados y una expiración.

    Args:
        data: Diccionario con los claims del token (ej: {"sub": "admin"})

    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    token = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token


def verificar_token(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependency de FastAPI que verifica el token JWT.
    Se usa como parámetro en los endpoints protegidos.

    Args:
        token: Token JWT extraído automáticamente del header Authorization

    Returns:
        El username (subject) del token

    Raises:
        HTTPException 401 si el token es inválido o ha expirado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception
