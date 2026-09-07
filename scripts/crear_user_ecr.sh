#!/bin/bash
set -euo pipefail

USERNAME="ecr-pull-user"
POLICY_NAME="ecr-pull-policy"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Crear el usuario
aws iam create-user --user-name ${USERNAME}

# Crear política de solo lectura para ECR
cat > /tmp/ecr-pull-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:DescribeImages",
                "ecr:DescribeRepositories",
                "ecr:ListImages"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Crear política
aws iam create-policy \
  --policy-name ${POLICY_NAME} \
  --policy-document file:///tmp/ecr-pull-policy.json

# Adjuntar política al usuario
aws iam attach-user-policy \
  --user-name ${USERNAME} \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}

# Crear access key para el usuario
aws iam create-access-key --user-name ${USERNAME} > /tmp/ecr-user-keys.json

echo "Usuario ${USERNAME} creado exitosamente"
echo "Access Key: $(cat /tmp/ecr-user-keys.json | jq -r '.AccessKey.AccessKeyId')"
echo "Secret Key: $(cat /tmp/ecr-user-keys.json | jq -r '.AccessKey.SecretAccessKey')"
echo "Guarda estas credenciales de forma segura"
