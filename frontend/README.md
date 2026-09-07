# V5 - React: Versión final con Tests

## ¿Qué cambió respecto a V4?
Se agregan **pruebas automatizadas** con Jest + React Testing Library:

| Archivo | Qué prueba |
|---------|-----------|
| `Display.test.tsx` | Renderizado encendido/apagado, loading, clases CSS |
| `NumberPad.test.tsx` | Clicks en números, punto, igual, estados disabled |
| `StatusBar.test.tsx` | Indicador de conexión, mensajes de error |
| `api.test.ts` | Login, sumar, dividir entre cero, token expirado (mock de fetch) |

## Estructura final completa
```
v5-tests/
├── .env
├── package.json
├── README.md
├── public/
│   └── index.html
├── src/
│   ├── App.tsx
│   ├── App.css
│   ├── Calculador.tsx              ← Orquestador
│   ├── Calculadora.css             ← Estilos de la calculadora
│   ├── index.tsx
│   ├── index.css
│   ├── assets/
│   │   └── image/mate.png
│   ├── components/
│   │   ├── index.ts
│   │   ├── Display.tsx
│   │   ├── NumberPad.tsx
│   │   ├── OperationPad.tsx
│   │   ├── StatusBar.tsx
│   │   └── Historial.tsx
│   ├── hooks/
│   │   ├── index.ts
│   │   ├── useAuth.ts
│   │   └── useCalculadora.ts
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   └── index.ts
│   ├── Display.test.tsx            ← Tests
│   ├── NumberPad.test.tsx
│   ├── StatusBar.test.tsx
│   └── api.test.ts
```

## Ejecutar tests
```bash
npm install
npm test
```

## Resumen de la evolución
| Versión | Qué agrega | Concepto clave |
|---------|-----------|----------------|
| V1 | Todo en un archivo | Conexión básica con la API |
| V2 | Componentes + service | Separación de responsabilidades |
| V3 | Custom hooks + .env | Lógica reutilizable, config externalizada |
| V4 | Errores tipados + historial | Robustez y UX |
| V5 | Tests automatizados | Calidad y confianza |

## Conexión con el backend
Todas las versiones se conectan al backend. Para la experiencia completa:

```bash
# Terminal 1: Backend (V6 recomendado para CORS)
cd taller-api-rest/v6-cors
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend (cualquier versión)
cd taller-react/v5-tests
npm install
npm start
```
