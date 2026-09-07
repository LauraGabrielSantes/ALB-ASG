# ============================================================
# Tests de la Calculadora
# ============================================================
# Cada test verifica:
# 1. Que el endpoint funcione correctamente (caso feliz)
# 2. Que retorne el resultado esperado
# 3. Que maneje errores correctamente
# 4. Que rechace peticiones sin token (401)
# ============================================================


class TestSumar:
    """Tests del endpoint POST /calculadora/sumar"""

    def test_suma_correcta(self, client, auth_headers):
        response = client.post(
            "/calculadora/sumar",
            json={"a": 10, "b": 5},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["resultado"] == 15
        assert data["operacion"] == "suma"

    def test_suma_numeros_negativos(self, client, auth_headers):
        response = client.post(
            "/calculadora/sumar",
            json={"a": -3, "b": -7},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["resultado"] == -10

    def test_suma_decimales(self, client, auth_headers):
        response = client.post(
            "/calculadora/sumar",
            json={"a": 0.1, "b": 0.2},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert round(response.json()["resultado"], 10) == round(0.3, 10)

    def test_suma_sin_token_retorna_401(self, client):
        """Sin token de autenticación debe retornar 401."""
        response = client.post(
            "/calculadora/sumar",
            json={"a": 1, "b": 2},
        )
        assert response.status_code == 401


class TestRestar:
    """Tests del endpoint POST /calculadora/restar"""

    def test_resta_correcta(self, client, auth_headers):
        response = client.post(
            "/calculadora/restar",
            json={"a": 10, "b": 3},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["resultado"] == 7

    def test_resta_resultado_negativo(self, client, auth_headers):
        response = client.post(
            "/calculadora/restar",
            json={"a": 3, "b": 10},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["resultado"] == -7

    def test_resta_sin_token_retorna_401(self, client):
        response = client.post(
            "/calculadora/restar",
            json={"a": 1, "b": 2},
        )
        assert response.status_code == 401


class TestMultiplicar:
    """Tests del endpoint POST /calculadora/multiplicar"""

    def test_multiplicacion_correcta(self, client, auth_headers):
        response = client.post(
            "/calculadora/multiplicar",
            json={"a": 4, "b": 5},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["resultado"] == 20

    def test_multiplicacion_por_cero(self, client, auth_headers):
        response = client.post(
            "/calculadora/multiplicar",
            json={"a": 100, "b": 0},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["resultado"] == 0

    def test_multiplicacion_sin_token_retorna_401(self, client):
        response = client.post(
            "/calculadora/multiplicar",
            json={"a": 1, "b": 2},
        )
        assert response.status_code == 401


class TestDividir:
    """Tests del endpoint POST /calculadora/dividir"""

    def test_division_correcta(self, client, auth_headers):
        response = client.post(
            "/calculadora/dividir",
            json={"a": 10, "b": 2},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["resultado"] == 5

    def test_division_con_decimales(self, client, auth_headers):
        response = client.post(
            "/calculadora/dividir",
            json={"a": 7, "b": 2},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["resultado"] == 3.5

    def test_division_entre_cero_retorna_400(self, client, auth_headers):
        """Dividir entre cero debe retornar error 400."""
        response = client.post(
            "/calculadora/dividir",
            json={"a": 10, "b": 0},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "cero" in response.json()["detail"].lower()

    def test_division_sin_token_retorna_401(self, client):
        response = client.post(
            "/calculadora/dividir",
            json={"a": 1, "b": 2},
        )
        assert response.status_code == 401


class TestValidacion:
    """Tests de validación de datos de entrada."""

    def test_campo_faltante_retorna_422(self, client, auth_headers):
        """Si falta un campo obligatorio, Pydantic retorna 422."""
        response = client.post(
            "/calculadora/sumar",
            json={"a": 10},  # falta "b"
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_tipo_incorrecto_retorna_422(self, client, auth_headers):
        """Si el tipo de dato es incorrecto, Pydantic retorna 422."""
        response = client.post(
            "/calculadora/sumar",
            json={"a": "no-soy-numero", "b": 5},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_body_vacio_retorna_422(self, client, auth_headers):
        """Si no se envía body, retorna 422."""
        response = client.post(
            "/calculadora/sumar",
            headers=auth_headers,
        )
        assert response.status_code == 422
