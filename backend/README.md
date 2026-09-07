# V6 - API-REST: Versión final con CORS

## ¿Qué cambió respecto a V5?
Se agrega **CORS (Cross-Origin Resource Sharing)** para que un frontend pueda consumir la API:

- `CORSMiddleware` configurado con orígenes específicos
- Orígenes configurables desde `.env`
- Tests de CORS incluidos

## ¿Qué es CORS y por qué lo necesitamos?
Cuando tu frontend en `localhost:3000` intenta llamar a tu API en `localhost:8000`, el navegador **bloquea la petición** por política de seguridad (Same-Origin Policy). CORS le dice al navegador: "estos orígenes están autorizados a comunicarse conmigo".

**Sin CORS** → El navegador muestra error y bloquea la respuesta.
**Con CORS** → El navegador permite la comunicación.

## Estructura final completa
```
v6-cors/
├── main.py                        ← Punto de entrada con CORS + logging
├── requirements.txt
├── .env                           ← Configuración (incluye orígenes CORS)
├── README.md
├── tests/
│   ├── conftest.py                ← Fixtures: client, auth_headers
│   ├── test_health.py
│   ├── test_auth.py
│   ├── test_calculadora.py
│   └── test_cors.py               ← NUEVO: tests de CORS
└── app/
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   ├── config.py              ← MODIFICADO: agrega CORS_ORIGINS
    │   ├── security.py
    │   ├── logger.py
    │   └── middleware.py
    ├── routers/
    │   ├── __init__.py
    │   ├── auth_router.py
    │   ├── calculadora_router.py
    │   └── health_router.py
    ├── schemas/
    │   ├── __init__.py
    │   ├── auth.py
    │   └── calculadora.py
    └── services/
        ├── __init__.py
        └── calculadora_service.py
```

## Ejecución
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Ejecutar tests
```bash
pytest -v
```

## Resumen de la evolución
| Versión | Qué agrega | Concepto clave |
|---------|-----------|----------------|
| V1 | Todo en un archivo | Conceptos básicos de FastAPI |
| V2 | Separación en capas | Arquitectura limpia (router/service/schema) |
| V3 | Autenticación JWT | Protección de endpoints con tokens |
| V4 | Logging estructurado | Observabilidad (qué pasa en la app) |
| V5 | Tests automatizados | Garantía de que funciona correctamente |
| V6 | CORS | Comunicación segura con el frontend |
