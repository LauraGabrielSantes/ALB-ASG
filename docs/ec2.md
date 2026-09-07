# AWS Elastic Cloud Computing (EC2)

En este paso se harán los siguientes pasos:

- Crear una instancia EC2 Ubuntu 24
- Asociarla a:
  - VPC
  - Subred pública
  - Security Group
- Asignar IP pública
- Asociar el rol IAM:
  ```text
  EC2-CodeDeploy-Role
  ```
- Instalar:
  - Docker
  - CodeDeploy Agent
  - AWS CLI

1. Variables utilizadas

    ```bash
    AWS_REGION="us-east-1"

    SUBNET_ID="subnet-xxxxxxxx"
    SECURITY_GROUP_ID="sg-xxxxxxxx"

    KEY_PAIR_NAME="mi-keypair"

    IAM_ROLE_NAME="EC2-CodeDeploy-Role"
    INSTANCE_PROFILE_NAME="EC2-CodeDeploy-Role"

    INSTANCE_NAME="MiEC2Ubuntu24"
    ```

2. Obtener la AMI de Ubuntu 24

    ```bash
    aws ssm get-parameters \
        --names /aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id \
        --region $AWS_REGION
    ```

    Resultado esperado:

    ```json
    {
        "Parameters": [
            {
                "Value": "ami-xxxxxxxxxxxxxxxxx"
            }
        ]
    }
    ```

    Guarda el valor:

    ```bash
    AMI_ID="ami-xxxxxxxxxxxxxxxxx"
    ```

3. Crear Instance Profile

    ```bash
    aws iam create-instance-profile \
        --instance-profile-name $INSTANCE_PROFILE_NAME
    ```

    **Asociar el rol al Instance Profile**

    ```bash
    aws iam add-role-to-instance-profile \
        --instance-profile-name $INSTANCE_PROFILE_NAME \
        --role-name $IAM_ROLE_NAME
    ```

4. Crear una llave SSH (Key Pair)

    La instancia EC2 utilizará una llave SSH para permitir acceso remoto seguro.

    ```bash
    aws ec2 create-key-pair \
        --key-name mi-keypair \
        --query 'KeyMaterial' \
        --output text > mi-keypair.pem
    ```

    **Asignar permisos seguros a la llave**

    ```bash
    chmod 400 mi-keypair.pem
    ```

    **Verificar que la llave fue creada**

    ```bash
    ls -l mi-keypair.pem
    ```


5. Crear la instancia EC2 **(Ubuntu 24)**

    ```bash
    aws ec2 run-instances \
        --image-id $AMI_ID \
        --instance-type t3.nano \
        --key-name $KEY_PAIR_NAME \
        --subnet-id $SUBNET_ID \
        --security-group-ids $SECURITY_GROUP_ID \
        --associate-public-ip-address \
        --iam-instance-profile Name=$INSTANCE_PROFILE_NAME \
        --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value='"$INSTANCE_NAME"'}]' \
        --region $AWS_REGION
    ```

6. Obtener el ID de la instancia

    ```bash
    aws ec2 describe-instances \
        --filters "Name=tag:Name,Values=$INSTANCE_NAME" \
        --query "Reservations[*].Instances[*].InstanceId" \
        --output text
    ```

    Ejemplo:

    ```bash
    INSTANCE_ID="i-xxxxxxxxxxxxxxxxx"
    ```

7. Obtener la IP pública

    ```bash
    aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --query "Reservations[*].Instances[*].PublicIpAddress" \
        --output text
    ```

    Resultado esperado:

    ```text
    44.xxx.xxx.xxx
    ```

8. Conectarse por SSH

    ```bash
    ssh -i mi-keypair.pem ubuntu@<PUBLIC_IP>
    ```

    Ejemplo:

    ```bash
    ssh -i mi-keypair.pem ubuntu@44.xxx.xxx.xxx
    ```

9. Instalar Docker

    ```bash
    sudo apt update
    sudo apt install -y ca-certificates curl gnupg ruby-full wget unzip

    sudo install -m 0755 -d /etc/apt/keyrings

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list

    sudo apt update

    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    sudo systemctl enable docker

    sudo usermod -aG docker ubuntu
    ```

10. Instalar CodeDeploy Agent

    ```bash
    wget https://aws-codedeploy-us-east-1.s3.us-east-1.amazonaws.com/latest/install

    chmod +x ./install

    sudo ./install auto

    sudo systemctl start codedeploy-agent

    sudo systemctl enable codedeploy-agent
    ```

11. Verificar CodeDeploy Agent

    ```bash
    sudo systemctl status codedeploy-agent
    ```


12. Instalar AWS CLI

    ```bash
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" \
    -o "awscliv2.zip"

    unzip awscliv2.zip

    sudo ./aws/install
    ```

13. Verificar AWS CLI

    ```bash
    aws --version
    ```

14. Verificar que el rol IAM funciona

    ```bash
    aws sts get-caller-identity
    ```

    Si todo está correcto, verás la identidad asociada al rol IAM.


15. Verificar Docker

    ```bash
    docker --version
    ```

16. Resultado esperado

    | Recurso | Configuración |
    |---|---|
    | Sistema operativo | Ubuntu 24 |
    | Tipo | t3.nano |
    | Red | Subred pública |
    | IP pública | Sí |
    | Security Group | SSH + puerto 3000 |
    | IAM Role | EC2-CodeDeploy-Role |
    | Docker | Instalado |
    | CodeDeploy Agent | Instalado |
    | AWS CLI | Instalado |

### [Regresar](./../README.md#guía-de-configuración)