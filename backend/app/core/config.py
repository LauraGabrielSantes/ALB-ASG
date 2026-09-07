# ============================================================
# Configuración centralizada
# ============================================================
# V6: Se agregan variables de CORS.
# En producción NUNCA usar allow_origins=["*"].
# Siempre listar los orígenes permitidos explícitamente.
# ============================================================

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación."""

    # --- App ---
    APP_NAME: str = "Calculadora API"
    APP_VERSION: str = "6.0.0"

    # --- JWT ---
    JWT_SECRET_KEY: str = "mi-clave-secreta-cambiar-en-produccion"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Usuarios de demo ---
    DEMO_USERNAME: str = "admin"
    DEMO_PASSWORD: str = "admin123"

    # --- CORS ---
    # En desarrollo puedes usar ["*"] pero en producción
    # SIEMPRE lista los orígenes específicos de tu frontend.
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",      # React dev server
        "http://localhost:5173",      # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    CORS_ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list[str] = ["Authorization", "Content-Type"]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
