# ============================================================
# Tests del Health Check
# ============================================================

def test_health_retorna_ok(client):
    """El health check debe retornar status 200 y status 'ok'."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
