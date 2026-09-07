# ============================================================
# Tests de CORS
# ============================================================
# Verificamos que la API responda con los headers CORS
# correctos cuando recibe una petición preflight (OPTIONS).
# ============================================================


def test_cors_preflight_origen_permitido(client):
    """Una petición preflight desde un origen permitido debe incluir headers CORS."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_cors_get_incluye_headers(client):
    """Una petición GET desde un origen permitido incluye headers CORS en la respuesta."""
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
