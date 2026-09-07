# AWS Identity and Access Managemente (IAM)

### Paso 0 - Autenticarse desde la AWS CLI

1. Abrir una terminal y ejecutar el comando siguiente:
    ```
    aws configure
    ```
2. Les pedira ingresar los siguientes datos, se debe llenar con los datos del archivo csv de su cuenta y en el campo región, para este ejemplo se utiliza *us-east-1*, en el formato de salida se deja vacio.
    ```
    AWS Access Key ID [None]:
    AWS Secret Access Key [None]:
    Default region name [None]:
    Default output format [None]:
    ```


### Paso 1 - Crear el proveedor OIDC de GitHub en AWS IAM

Esto le dice a AWS: _"confío en los tokens que emite GitHub Actions"_.

1. En una terminal se debe ejecutar el siguiente comando:
    ```
    aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --client-id-list sts.amazonaws.com
    ```

2. ¿Qué hace cada parámetro?

    | Parámetro | Descripción |
    | --- | --- |
    | **--url** | URL oficial del proveedor OIDC de GitHub Actions
    | **--client-id-list** | Servicio autorizado para solicitar tokens (sts.amazonaws.com)

3. Verificar que se creó correctamente. Lista los proveedores OIDC:
    ```
    aws iam list-open-id-connect-providers
    ```
### Paso 2 - Crear políticas necesarias

**CodeDeploy-GitHubActions-Policy**

La política será utilizada posteriormente por un rol IAM para permitir que GitHub Actions despliegue aplicaciones usando AWS CodeDeploy.

1. Crea un archivo llamado *codedeploy-github-actions-policy.json* con el siguiente comando:

    ```bash
    cat <<EOF > codedeploy-github-actions-policy.json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "CodeDeployPermissions",
                "Effect": "Allow",
                "Action": [
                    "codedeploy:CreateDeployment",
                    "codedeploy:GetDeployment",
                    "codedeploy:GetDeploymentConfig",
                    "codedeploy:RegisterApplicationRevision",
                    "codedeploy:GetApplicationRevision"
                ],
                "Resource": "*"
            }
        ]
    }
    EOF
    ```

2. Crear la política IAM

    Ejecuta el siguiente comando:

    ```bash
    aws iam create-policy \
        --policy-name CodeDeploy-GitHubActions-Policy \
        --policy-document file://codedeploy-github-actions-policy.json
    ```

3. Verificar que la política fue creada

    ```bash
    aws iam list-policies \
        --scope Local
    ```

    También puedes obtener los detalles específicos:

    ```bash
    aws iam get-policy \
        --policy-arn arn:aws:iam::<AWS_ACCOUNT_ID>:policy/CodeDeploy-GitHubActions-Policy
    ```

    Reemplaza:

    ```text
    <AWS_ACCOUNT_ID>
    ```

    por tu ID de cuenta AWS.

### Repetir los pasos con las siguientes dos políticas

**ECR-GitHubActions-Policy**

1. Crea un archivo llamado *ecr-github-actions-policy.json* con el siguiente comando:
    ```bash
    cat <<EOF > ecr-github-actions-policy.json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ECRAuth",
                "Effect": "Allow",
                "Action": [
                    "ecr:GetAuthorizationToken"
                ],
                "Resource": "*"
            },
            {
                "Sid": "ECRPush",
                "Effect": "Allow",
                "Action": [
                    "ecr:BatchGetImage",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:CompleteLayerUpload",
                    "ecr:InitiateLayerUpload",
                    "ecr:PutImage",
                    "ecr:UploadLayerPart"
                ],
                "Resource": "*"
            }
        ]
    }
    EOF
    ```

2. Ejecuta el siguiente comando:

    ```bash
    aws iam create-policy \
        --policy-name ECR-GitHubActions-Policy \
        --policy-document file://ecr-github-actions-policy.json
    ```

3. Verificar que la política fue creada

    ```bash
    aws iam list-policies \
        --scope Local
    ```

**S3-GitHubActions-CodeDeploy-Policy**

1. Crea un archivo llamado *s3-github-actions-policy.json* con el siguiente comando:
    ```bash
    cat <<EOF > s3-github-actions-policy.json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "UploadArtifacts",
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject"
                ],
                "Resource": "*"
            }
        ]
    }
    EOF
    ```

2. Ejecuta el siguiente comando:

    ```bash
    aws iam create-policy \
        --policy-name S3-GitHubActions-Policy \
        --policy-document file://s3-github-actions-policy.json
    ```

3. Verificar que la política fue creada

    ```bash
    aws iam list-policies \
        --scope Local
    ```

### Paso 3 - Crear el rol IAM que GitHub Actions va a asumir

Este rol define qué puede hacer GitHub Actions dentro de tu cuenta AWS.

1. Crear la Trust Policy con el siguiente comando:

    ```bash
    cat <<EOF > trust-policy.json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
                },
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                    },
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": "repo:<GITHUB_ORG o GITHUB_USER>/<GITHUB_REPOSITORY>:*"
                    }
                }
            }
        ]
    }
    EOF
    ```

2. Crear el rol IAM con el siguiente comando:
    ```bash
    aws iam create-role \
        --role-name GitHubActionsDeployRole \
        --assume-role-policy-document file://trust-policy.json
    ```

3. Asociar las políticas al rol

    - Asociar política de CodeDeploy
        ```bash
        aws iam attach-role-policy \
            --role-name GitHubActionsDeployRole \
            --policy-arn arn:aws:iam::<AWS_ACCOUNT_ID>:policy/CodeDeploy-GitHubActions-Policy
        ```
    - Asociar política de S3
        ```bash
        aws iam attach-role-policy \
            --role-name GitHubActionsDeployRole \
            --policy-arn arn:aws:iam::<AWS_ACCOUNT_ID>:policy/S3-GitHubActions-Policy
        ```
    - Asociar política de ECR
        ```bash
        aws iam attach-role-policy \
            --role-name GitHubActionsDeployRole \
            --policy-arn arn:aws:iam::<AWS_ACCOUNT_ID>:policy/ECR-GitHubActions-Policy
        ```
    - Asociar política de AmazonEC2ContainerRegistryPullOnly
        ```bash
        aws iam attach-role-policy \
            --role-name GitHubActionsDeployRole \
            --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly
        ```

    - Asociar política de AmazonEC2ContainerRegistryReadOnly
        ```bash
        aws iam attach-role-policy \
            --role-name GitHubActionsDeployRole \
            --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
        ```

    - Asociar política de AWSCodeDeployRole
        ```bash
        aws iam attach-role-policy \
            --role-name GitHubActionsDeployRole \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole
        ```

4. Verificar el rol

    ```bash
    aws iam get-role \
        --role-name GitHubActionsDeployRole
    ```

5. Verificar las políticas asociadas

    ```bash
    aws iam list-attached-role-policies \
        --role-name GitHubActionsDeployRole
    ```

6. Restringir acceso a una rama específica

    - Actualmente:

        ```json
        "token.actions.githubusercontent.com:sub": "repo:<GITHUB_ORG>/<GITHUB_REPOSITORY>:*"
        ```
        permite cualquier rama.

        Para restringir únicamente a `main`, reemplaza por:

        ```json
        "token.actions.githubusercontent.com:sub": "repo:<GITHUB_ORG>/<GITHUB_REPOSITORY>:ref:refs/heads/main"
        ```

7. Resultado esperado, el rol:
    ```text
    GitHubActionsDeployRole
    ```

    podrá ser asumido únicamente desde:

    - El repositorio especificado
    - GitHub Actions
    - La rama configurada
    - Mediante OIDC

8. Obtener el ARN del rol

    ```bash
    aws iam get-role \
        --role-name GitHubActionsDeployRole \
        --query "Role.Arn" \
        --output text
    ```

    Resultado esperado:

    ```text
    arn:aws:iam::123456789012:role/GitHubActionsDeployRole
    ```

    Este ARN será utilizado posteriormente en GitHub Actions.

9. Reemplazar variables

    | Variable | Descripción |
    |---|---|
    | `<AWS_ACCOUNT_ID>` | ID de tu cuenta AWS |
    | `<GITHUB_ORG>` | Usuario u organización de GitHub |
    | `<GITHUB_REPOSITORY>` | Nombre del repositorio |

### Paso 4 - Crear un rol para la instancia de EC2

El rol será utilizado por la instancia EC2 para:

- Descargar imágenes desde Amazon ECR
- Leer artefactos desde Amazon S3
- Trabajar con AWS CodeDeploy

1. Crear la Trust Policy con el siguiente comando:

    ```bash
    cat <<EOF > ec2-trust-policy.json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    EOF
    ```

2. Crear el rol IAM

    ```bash
    aws iam create-role \
        --role-name EC2-CodeDeploy-Role \
        --assume-role-policy-document file://ec2-trust-policy.json
    ```

3. Asociar políticas al rol

    - **AmazonEC2ContainerRegistryReadOnly**

        ```bash
        aws iam attach-role-policy \
            --role-name EC2-CodeDeploy-Role \
            --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
        ```

    - **AmazonS3ReadOnlyAccess**

        ```bash
        aws iam attach-role-policy \
            --role-name EC2-CodeDeploy-Role \
            --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
        ```

    - **AWSCodeDeployFullAccess** (necesario para que el agente reporte el estado del despliegue)

        ```bash
        aws iam attach-role-policy \
            --role-name EC2-CodeDeploy-Role \
            --policy-arn arn:aws:iam::aws:policy/AWSCodeDeployFullAccess
        ```

4. Verificar políticas asociadas

    ```bash
    aws iam list-attached-role-policies \
        --role-name EC2-CodeDeploy-Role
    ```

### [Regresar](./../README.md#guía-de-configuración)