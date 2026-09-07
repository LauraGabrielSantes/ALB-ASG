# Automatizacion CI/CD - flujo de prueba 6.6 - despliegue via CodeDeploy
# ============================================================
# V6 - API-REST: Incluye CORS (versión final)
# ============================================================
# Cambios respecto a V5:
#   - Se agrega CORSMiddleware de FastAPI
#   - Los orígenes permitidos se configuran desde .env
#   - Ahora un frontend (React, Vue, etc.) puede consumir la API
#
# ¿Qué es CORS?
# El navegador bloquea peticiones de un origen (ej: localhost:3000)
# a otro origen (ej: localhost:8000) por seguridad.
# CORS le dice al navegador: "estos orígenes sí pueden acceder".
#
# Sin CORS → el frontend recibe error en el navegador.
# Con CORS → el navegador permite la comunicación.
# ============================================================

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import logger
from app.core.middleware import LoggingMiddleware
from app.routers import calculadora_router, health_router, auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Calculadora API v6.0.0 iniciada (versión final)")
    logger.info(f"CORS habilitado para: {settings.CORS_ORIGINS}")
    yield
    logger.info("Calculadora API apagada")


app = FastAPI(
    title="Calculadora API",
    description="API REST de calculadora - V6: Versión final con CORS",
    version="6.0.0",
    root_path="/api",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# --- CORS ---
# IMPORTANTE: CORSMiddleware debe ir ANTES del LoggingMiddleware
# para que las peticiones preflight (OPTIONS) se manejen correctamente.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# --- Logging ---
app.add_middleware(LoggingMiddleware)

# --- Routers ---
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(calculadora_router)
