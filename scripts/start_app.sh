#!/bin/bash

set -euo pipefail

# Despliega la imagen indicada por el workflow o por el entorno
APP_VERSION="${APP_VERSION:-latest}"
export APP_VERSION

cd /opt/mi-app

# Usa la región del entorno o el valor por defecto del despliegue
AWS_REGION="${AWS_REGION:-us-east-1}"
export AWS_REGION

# Usa el registro ECR inyectado por el workflow.
# Si no llega, se deriva desde el rol de la instancia.
ECR_REGISTRY="${ECR_REGISTRY:-}"

if [[ -z "$ECR_REGISTRY" ]]; then
    ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
    ECR_REGISTRY="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
fi

export ECR_REGISTRY

# Autentica Docker con ECR usando el rol de la instancia
# (sin credenciales hardcodeadas)
aws ecr get-login-password --region "$AWS_REGION" | \
    docker login --username AWS --password-stdin \
    "$ECR_REGISTRY"

# Usa el archivo Compose del despliegue HTTP por defecto
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
export COMPOSE_FILE

# Descarga las nuevas imágenes (backend + frontend)
docker compose -f "$COMPOSE_FILE" pull

# Detiene los contenedores actuales
docker compose -f "$COMPOSE_FILE" down --remove-orphans

# Levanta los nuevos contenedores
docker compose -f "$COMPOSE_FILE" up -d

# Limpia imágenes antiguas para no llenar el disco
docker image prune -f
