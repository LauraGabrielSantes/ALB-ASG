# ============================================================
# Tests de Autenticación
# ============================================================


def test_login_exitoso(client):
    """Login con credenciales correctas retorna un token."""
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_credenciales_incorrectas(client):
    """Login con credenciales incorrectas retorna 401."""
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "password-malo"},
    )
    assert response.status_code == 401
    assert "Credenciales incorrectas" in response.json()["detail"]


def test_login_usuario_inexistente(client):
    """Login con usuario que no existe retorna 401."""
    response = client.post(
        "/auth/login",
        data={"username": "noexisto", "password": "admin123"},
    )
    assert response.status_code == 401
