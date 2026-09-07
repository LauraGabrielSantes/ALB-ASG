# AWS Elastic Container Repository (ECR)

En esta sección se realizarán los siguientes pasos:

- Crear el repositorio del frontend
- Crear el repositorio del backend
- Verificar los repositorios
- Guardar las URIs para usarlas más adelante

**Variables utilizadas**

```bash
AWS_REGION="us-east-1"

FRONTEND_REPO="calculadora/frontend"
BACKEND_REPO="calculadora/backend"
```

1. Crear el repositorio del frontend

    ```bash
    aws ecr create-repository \
        --repository-name $FRONTEND_REPO \
        --region $AWS_REGION
    ```

    Resultado esperado:

    ```json
    {
        "repository": {
            "repositoryUri": "123456789012.dkr.ecr.us-east-1.amazonaws.com/calculadora/frontend"
        }
    }
    ```

    Guarda la URI:

    ```bash
    FRONTEND_URI="123456789012.dkr.ecr.us-east-1.amazonaws.com/calculadora/frontend"
    ```

2. Crear el repositorio del backend

    ```bash
    aws ecr create-repository \
        --repository-name $BACKEND_REPO \
        --region $AWS_REGION
    ```

    Resultado esperado:

    ```json
    {
        "repository": {
            "repositoryUri": "123456789012.dkr.ecr.us-east-1.amazonaws.com/calculadora/backend"
        }
    }
    ```

    Guarda la URI:

    ```bash
    BACKEND_URI="123456789012.dkr.ecr.us-east-1.amazonaws.com/calculadora/backend"
    ```

3. Verificar los repositorios

    ```bash
    aws ecr describe-repositories --region $AWS_REGION
    ```

    También puedes consultar ambos repositorios individualmente:

    ```bash
    aws ecr describe-repositories \
        --repository-names $FRONTEND_REPO $BACKEND_REPO \
        --region $AWS_REGION
    ```

4. Construir la variable de registro (ECR Registry)

    La URI de registro es el prefijo común a todos los repositorios y se forma con el ID de cuenta y la región:

    ```bash
    ECR_REGISTRY="<AWS_ACCOUNT_ID>.dkr.ecr.$AWS_REGION.amazonaws.com"
    ```

    Reemplaza `<AWS_ACCOUNT_ID>` por tu ID de cuenta AWS. Este valor se usará como variable de entorno en el `docker-compose.yml` y en el script de despliegue.

5. Resultado esperado

    | Recurso | URI |
    |---|---|
    | Repositorio frontend | `<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/calculadora/frontend` |
    | Repositorio backend | `<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/calculadora/backend` |
    | ECR Registry | `<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com` |

### [Regresar](./../README.md#guía-de-configuración)
