# AWS Virtual Private Cloud (VPC)

Se deben crear los siguientes recursos:

- VPC
- Subred pública
- Internet Gateway
- Route Table
- Asociación de rutas
- Security Group

Define algunas variables para reutilizar comandos:

```bash
AWS_REGION="us-east-1"

VPC_CIDR="10.0.0.0/16"
SUBNET_CIDR="10.0.1.0/24"

VPC_NAME="gh-vpc"
SUBNET_NAME="gh-subnet"
IGW_NAME="gh-gateway"
ROUTE_TABLE_NAME="gh-route-table"
SECURITY_GROUP_NAME="gh-security-group"
```

1. Crear VPC

    ```bash
    aws ec2 create-vpc \
        --cidr-block $VPC_CIDR \
        --region $AWS_REGION
    ```

    Resultado esperado:

    ```json
    {
        "Vpc": {
            "VpcId": "vpc-xxxxxxxx"
        }
    }
    ```

    Guarda el `VpcId`.

    Ejemplo:

    ```bash
    VPC_ID="vpc-xxxxxxxx"
    ```

    **Habilitar DNS en la VPC**

    ```bash
    aws ec2 modify-vpc-attribute \
        --vpc-id $VPC_ID \
        --enable-dns-support "{\"Value\":true}"
    ```

    ```bash
    aws ec2 modify-vpc-attribute \
        --vpc-id $VPC_ID \
        --enable-dns-hostnames "{\"Value\":true}"
    ```

    **Agregar nombre a la VPC**

    ```bash
    aws ec2 create-tags \
        --resources $VPC_ID \
        --tags Key=Name,Value=$VPC_NAME
    ```

2. Crear subred pública

    ```bash
    aws ec2 create-subnet \
        --vpc-id $VPC_ID \
        --cidr-block $SUBNET_CIDR \
        --availability-zone us-east-1a
    ```

    Resultado esperado:

    ```json
    {
        "Subnet": {
            "SubnetId": "subnet-xxxxxxxx"
        }
    }
    ```

    Guarda el `SubnetId`.

    ```bash
    SUBNET_ID="subnet-xxxxxxxx"
    ```

    **Habilitar IP pública automática**

    ```bash
    aws ec2 modify-subnet-attribute \
        --subnet-id $SUBNET_ID \
        --map-public-ip-on-launch
    ```

    **Agregar nombre a la subred**

    ```bash
    aws ec2 create-tags \
        --resources $SUBNET_ID \
        --tags Key=Name,Value=$SUBNET_NAME
    ```

3. Crear Internet Gateway

    ```bash
    aws ec2 create-internet-gateway
    ```

    Resultado esperado:

    ```json
    {
        "InternetGateway": {
            "InternetGatewayId": "igw-xxxxxxxx"
        }
    }
    ```

    Guarda el `InternetGatewayId`.

    ```bash
    IGW_ID="igw-xxxxxxxx"
    ```

    Agregar nombre al Internet Gateway

    ```bash
    aws ec2 create-tags \
        --resources $IGW_ID \
        --tags Key=Name,Value=$IGW_NAME
    ```

    **Asociar Internet Gateway a la VPC**

    ```bash
    aws ec2 attach-internet-gateway \
        --internet-gateway-id $IGW_ID \
        --vpc-id $VPC_ID
    ```

4. Crear Route Table

    ```bash
    aws ec2 create-route-table \
        --vpc-id $VPC_ID
    ```

    Resultado esperado:

    ```json
    {
        "RouteTable": {
            "RouteTableId": "rtb-xxxxxxxx"
        }
    }
    ```

    Guarda el `RouteTableId`.

    ```bash
    ROUTE_TABLE_ID="rtb-xxxxxxxx"
    ```

    **Agregar nombre a la Route Table**

    ```bash
    aws ec2 create-tags \
        --resources $ROUTE_TABLE_ID \
        --tags Key=Name,Value=$ROUTE_TABLE_NAME
    ```

    **Crear ruta hacia Internet Gateway**

    ```bash
    aws ec2 create-route \
        --route-table-id $ROUTE_TABLE_ID \
        --destination-cidr-block 0.0.0.0/0 \
        --gateway-id $IGW_ID
    ```

    **Asociar Route Table a la subred**

    ```bash
    aws ec2 associate-route-table \
        --subnet-id $SUBNET_ID \
        --route-table-id $ROUTE_TABLE_ID
    ```

5. Crear Security Group

    ```bash
    aws ec2 create-security-group \
        --group-name $SECURITY_GROUP_NAME \
        --description "Security group para SSH y aplicacion" \
        --vpc-id $VPC_ID
    ```

    Resultado esperado:

    ```json
    {
        "GroupId": "sg-xxxxxxxx"
    }
    ```

    Guarda el `GroupId`.

    ```bash
    SECURITY_GROUP_ID="sg-xxxxxxxx"
    ```

6. Abrir puerto 22 para SSH

    ```bash
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0
    ```

7. Abrir puerto 3000 para la aplicación

    ```bash
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 3000 \
        --cidr 0.0.0.0/0
    ```

8. Verificar reglas del Security Group

    ```bash
    aws ec2 describe-security-groups \
        --group-ids $SECURITY_GROUP_ID
    ```

9. Resultado esperado

    | Recurso | Descripción |
    |---|---|
    | VPC | Red privada virtual |
    | Subred pública | Subred con acceso a Internet |
    | Internet Gateway | Salida a Internet |
    | Route Table | Ruta hacia Internet |
    | Security Group | Reglas de firewall |
    | Puerto 22 | Acceso SSH |
    | Puerto 3000 | Aplicación web |

### [Regresar](./../README.md#guía-de-configuración)