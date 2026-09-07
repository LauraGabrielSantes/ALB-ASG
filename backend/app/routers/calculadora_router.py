# ============================================================
# Router de Calculadora (PROTEGIDO con JWT)
# ============================================================
# La diferencia con V2: todos los endpoints ahora requieren
# un token JWT válido. Se agrega el parámetro:
#   current_user: str = Depends(verificar_token)
#
# FastAPI automáticamente:
# 1. Extrae el token del header Authorization
# 2. Lo valida con nuestra función verificar_token
# 3. Retorna 401 si no es válido
# 4. Pasa el username al endpoint si es válido
# ============================================================

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import verificar_token
from app.schemas import OperacionRequest, OperacionResponse, ErrorResponse
from app.services import CalculadoraService

router = APIRouter(
    prefix="/calculadora",
    tags=["Operaciones"],
)

service = CalculadoraService()


@router.post(
    "/sumar",
    response_model=OperacionResponse,
    summary="Sumar dos números",
)
def sumar(
    datos: OperacionRequest,
    current_user: str = Depends(verificar_token),  # ← Protección JWT
):
    """Realiza la suma de dos números. **Requiere autenticación.**"""
    resultado = service.sumar(datos.a, datos.b)
    return OperacionResponse(
        operacion="suma", a=datos.a, b=datos.b, resultado=resultado
    )


@router.post(
    "/restar",
    response_model=OperacionResponse,
    summary="Restar dos números",
)
def restar(
    datos: OperacionRequest,
    current_user: str = Depends(verificar_token),
):
    """Realiza la resta de dos números (a - b). **Requiere autenticación.**"""
    resultado = service.restar(datos.a, datos.b)
    return OperacionResponse(
        operacion="resta", a=datos.a, b=datos.b, resultado=resultado
    )


@router.post(
    "/multiplicar",
    response_model=OperacionResponse,
    summary="Multiplicar dos números",
)
def multiplicar(
    datos: OperacionRequest,
    current_user: str = Depends(verificar_token),
):
    """Realiza la multiplicación de dos números. **Requiere autenticación.**"""
    resultado = service.multiplicar(datos.a, datos.b)
    return OperacionResponse(
        operacion="multiplicacion", a=datos.a, b=datos.b, resultado=resultado
    )


@router.post(
    "/dividir",
    response_model=OperacionResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Dividir dos números",
)
def dividir(
    datos: OperacionRequest,
    current_user: str = Depends(verificar_token),
):
    """Realiza la división de dos números (a / b). **Requiere autenticación.**"""
    try:
        resultado = service.dividir(datos.a, datos.b)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return OperacionResponse(
        operacion="division", a=datos.a, b=datos.b, resultado=resultado
    )
