# ============================================================
# Fixtures de prueba
# ============================================================
# conftest.py es un archivo especial de pytest que contiene
# fixtures compartidas entre todos los archivos de test.
#
# Fixtures:
# - client: cliente HTTP para hacer peticiones al API sin
#   levantar un servidor real (TestClient de FastAPI)
# - auth_headers: headers con un token JWT válido para
#   testear endpoints protegidos
# ============================================================

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Cliente HTTP de prueba. No levanta un servidor real."""
    return TestClient(app, root_path="/api")


@pytest.fixture
def auth_headers(client):
    """
    Headers con token JWT válido.
    Hace login y retorna los headers listos para usar.
    """
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
