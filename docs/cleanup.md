# Eliminación de recursos

Esta guía elimina **todos** los recursos creados a lo largo de las guías anteriores en el orden correcto para evitar errores de dependencia.

> **Advertencia**: estas acciones son irreversibles. Verifica que no necesitas ningún recurso antes de continuar.

**Variables utilizadas**

```bash
AWS_REGION="us-east-1"

# IAM
OIDC_PROVIDER_ARN="arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
GITHUB_ACTIONS_ROLE="GitHubActionsDeployRole"
EC2_ROLE="EC2-CodeDeploy-Role"
CODEDEPLOY_SERVICE_ROLE="CodeDeployServiceRole"
INSTANCE_PROFILE_NAME="EC2-CodeDeploy-Role"

# ECR
FRONTEND_REPO="calculadora/frontend"
BACKEND_REPO="calculadora/backend"

# S3
S3_BUCKET="mi-app-codedeploy-NOMBRE-UNICO"

# VPC (obtener desde la consola o con describe)
VPC_ID="vpc-xxxxxxxx"
SUBNET_ID="subnet-xxxxxxxx"
IGW_ID="igw-xxxxxxxx"
ROUTE_TABLE_ID="rtb-xxxxxxxx"
SECURITY_GROUP_ID="sg-xxxxxxxx"

# EC2
INSTANCE_ID="i-xxxxxxxxxxxxxxxxx"
KEY_PAIR_NAME="mi-keypair"

# CodeDeploy
APPLICATION_NAME="mi-app"
DEPLOYMENT_GROUP_NAME="produccion"
```

---

## Paso 1 - Eliminar la aplicación de CodeDeploy

1. Eliminar el Deployment Group

    ```bash
    aws deploy delete-deployment-group \
        --application-name $APPLICATION_NAME \
        --deployment-group-name $DEPLOYMENT_GROUP_NAME \
        --region $AWS_REGION
    ```

2. Eliminar la aplicación

    ```bash
    aws deploy delete-application \
        --application-name $APPLICATION_NAME \
        --region $AWS_REGION
    ```

3. Verificar que la aplicación fue eliminada

    ```bash
    aws deploy list-applications --region $AWS_REGION
    ```

---

## Paso 2 - Terminar la instancia EC2

1. Terminar la instancia

    ```bash
    aws ec2 terminate-instances \
        --instance-ids $INSTANCE_ID \
        --region $AWS_REGION
    ```

2. Esperar a que la instancia esté terminada

    ```bash
    aws ec2 wait instance-terminated \
        --instance-ids $INSTANCE_ID \
        --region $AWS_REGION
    ```

3. Eliminar el Key Pair

    ```bash
    aws ec2 delete-key-pair \
        --key-name $KEY_PAIR_NAME \
        --region $AWS_REGION
    ```

    También elimina el archivo local:

    ```bash
    rm -f $KEY_PAIR_NAME.pem
    ```

---

## Paso 3 - Eliminar los recursos de red (VPC)

Los recursos deben eliminarse en orden ya que existen dependencias entre ellos.

1. Eliminar el Security Group

    ```bash
    aws ec2 delete-security-group \
        --group-id $SECURITY_GROUP_ID \
        --region $AWS_REGION
    ```

2. Desasociar la Route Table de la subred

    Obtén el ID de asociación:

    ```bash
    aws ec2 describe-route-tables \
        --route-table-ids $ROUTE_TABLE_ID \
        --query "RouteTables[*].Associations[*].RouteTableAssociationId" \
        --output text
    ```

    ```bash
    ASSOCIATION_ID="rtbassoc-xxxxxxxx"
    ```

    Desasocia:

    ```bash
    aws ec2 disassociate-route-table \
        --association-id $ASSOCIATION_ID
    ```

3. Eliminar la Route Table

    ```bash
    aws ec2 delete-route-table \
        --route-table-id $ROUTE_TABLE_ID \
        --region $AWS_REGION
    ```

4. Desconectar el Internet Gateway de la VPC

    ```bash
    aws ec2 detach-internet-gateway \
        --internet-gateway-id $IGW_ID \
        --vpc-id $VPC_ID \
        --region $AWS_REGION
    ```

5. Eliminar el Internet Gateway

    ```bash
    aws ec2 delete-internet-gateway \
        --internet-gateway-id $IGW_ID \
        --region $AWS_REGION
    ```

6. Eliminar la subred

    ```bash
    aws ec2 delete-subnet \
        --subnet-id $SUBNET_ID \
        --region $AWS_REGION
    ```

7. Eliminar la VPC

    ```bash
    aws ec2 delete-vpc \
        --vpc-id $VPC_ID \
        --region $AWS_REGION
    ```

8. Verificar que la VPC fue eliminada

    ```bash
    aws ec2 describe-vpcs \
        --filters "Name=vpc-id,Values=$VPC_ID" \
        --region $AWS_REGION
    ```

    El resultado debe estar vacío.

---

## Paso 4 - Vaciar y eliminar el bucket S3

1. Vaciar el bucket (elimina todos los objetos y versiones)

    ```bash
    aws s3 rm s3://$S3_BUCKET --recursive
    ```

2. Eliminar el bucket

    ```bash
    aws s3 rb s3://$S3_BUCKET --region $AWS_REGION
    ```

3. Verificar que el bucket fue eliminado

    ```bash
    aws s3 ls | grep $S3_BUCKET
    ```

    El resultado debe estar vacío.

---

## Paso 5 - Eliminar los repositorios de ECR

> **Advertencia**: el flag `--force` elimina el repositorio aunque contenga imágenes.

1. Eliminar el repositorio del frontend

    ```bash
    aws ecr delete-repository \
        --repository-name $FRONTEND_REPO \
        --force \
        --region $AWS_REGION
    ```

2. Eliminar el repositorio del backend

    ```bash
    aws ecr delete-repository \
        --repository-name $BACKEND_REPO \
        --force \
        --region $AWS_REGION
    ```

3. Verificar que los repositorios fueron eliminados

    ```bash
    aws ecr describe-repositories --region $AWS_REGION
    ```

---

## Paso 6 - Eliminar los roles y políticas de IAM

Los roles deben tener todas sus políticas desasociadas antes de poder eliminarse.

### GitHubActionsDeployRole

1. Desasociar las políticas del rol

    ```bash
    aws iam detach-role-policy \
        --role-name $GITHUB_ACTIONS_ROLE \
        --policy-arn arn:aws:iam::<AWS_ACCOUNT_ID>:policy/CodeDeploy-GitHubActions-Policy

    aws iam detach-role-policy \
        --role-name $GITHUB_ACTIONS_ROLE \
        --policy-arn arn:aws:iam::<AWS_ACCOUNT_ID>:policy/ECR-GitHubActions-Policy

    aws iam detach-role-policy \
        --role-name $GITHUB_ACTIONS_ROLE \
        --policy-arn arn:aws:iam::<AWS_ACCOUNT_ID>:policy/S3-GitHubActions-Policy

    aws iam detach-role-policy \
        --role-name $GITHUB_ACTIONS_ROLE \
        --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly

    aws iam detach-role-policy \
        --role-name $GITHUB_ACTIONS_ROLE \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole
    ```

2. Eliminar el rol

    ```bash
    aws iam delete-role \
        --role-name $GITHUB_ACTIONS_ROLE
    ```

### EC2-CodeDeploy-Role

1. Quitar el rol del Instance Profile

    ```bash
    aws iam remove-role-from-instance-profile \
        --instance-profile-name $INSTANCE_PROFILE_NAME \
        --role-name $EC2_ROLE
    ```

2. Eliminar el Instance Profile

    ```bash
    aws iam delete-instance-profile \
        --instance-profile-name $INSTANCE_PROFILE_NAME
    ```

3. Desasociar las políticas del rol

    ```bash
    aws iam detach-role-policy \
        --role-name $EC2_ROLE \
        --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly

    aws iam detach-role-policy \
        --role-name $EC2_ROLE \
        --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

    aws iam detach-role-policy \
        --role-name $EC2_ROLE \
        --policy-arn arn:aws:iam::aws:policy/AWSCodeDeployFullAccess
    ```

4. Eliminar el rol

    ```bash
    aws iam delete-role \
        --role-name $EC2_ROLE
    ```

### CodeDeployServiceRole

1. Desasociar la política del rol

    ```bash
    aws iam detach-role-policy \
        --role-name $CODEDEPLOY_SERVICE_ROLE \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole
    ```

2. Eliminar el rol

    ```bash
    aws iam delete-role \
        --role-name $CODEDEPLOY_SERVICE_ROLE
    ```

### Políticas personalizadas

```bash
aws iam delete-policy \
    --policy-arn arn:aws:iam::<AWS_ACCOUNT_ID>:policy/CodeDeploy-GitHubActions-Policy

aws iam delete-policy \
    --policy-arn arn:aws:iam::<AWS_ACCOUNT_ID>:policy/ECR-GitHubActions-Policy

aws iam delete-policy \
    --policy-arn arn:aws:iam::<AWS_ACCOUNT_ID>:policy/S3-GitHubActions-Policy
```

### Proveedor OIDC de GitHub

```bash
aws iam delete-open-id-connect-provider \
    --open-id-connect-provider-arn $OIDC_PROVIDER_ARN
```

Verificar que fue eliminado:

```bash
aws iam list-open-id-connect-providers
```

---

## Resultado esperado

| Recurso | Estado |
|---|---|
| Aplicación CodeDeploy | Eliminada |
| Deployment Group | Eliminado |
| Instancia EC2 | Terminada |
| Key Pair | Eliminado |
| Security Group | Eliminado |
| Route Table | Eliminada |
| Internet Gateway | Eliminado |
| Subred | Eliminada |
| VPC | Eliminada |
| Bucket S3 | Eliminado |
| Repositorios ECR | Eliminados |
| Roles IAM | Eliminados |
| Políticas IAM | Eliminadas |
| Proveedor OIDC | Eliminado |

### [Regresar](./../README.md#guía-de-configuración)
