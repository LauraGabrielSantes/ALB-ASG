#!/bin/bash
# Fase 9 (demo de rollback): este sleep es INTENCIONAL.
# Sin él, el despliegue es tan rápido (~2 min con WITHOUT_TRAFFIC_CONTROL) que la
# alarma 5xx (~2.5-3 min de latencia) llega DESPUÉS de que el despliegue haga
# Succeeded, y la versión mala queda como "última exitosa" (no hay rollback).
# Con este sleep, el despliegue sigue "InProgress" mientras la versión mala ya
# sirve /boom (500) -> la alarma gh-alb-5xx dispara a mitad y CodeDeploy revierte.
set -e

sleep 300

# Validación real (opcional): la app debe seguir respondiendo 200 en /api/health.
# Nota: /api/health debe seguir en 200 (si no, el ASG reemplazaría la instancia).
curl -fsS http://127.0.0.1:3000/api/health >/dev/null

echo "validate_service: OK"
