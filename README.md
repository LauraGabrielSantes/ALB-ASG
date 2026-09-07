# ALB-ASG
# Guía paso a paso: VPC + ALB + ASG + CodeDeploy en AWS

Guía de replicación basada en `guia-practica-aws-vpc-asg-codedeploy.md`.
Objetivo: implementar en AWS una VPC con balanceo de carga mediante **Application Load Balancer** y **Auto Scaling Group**.

---

## Arquitectura objetivo

```
Internet ──HTTP:80──► Application Load Balancer (web-demo-alb)
                        │ HTTP:3000
                        ▼
        EC2 en ASG (web-app-asg) ── Subredes públicas A/B
          └─ Contenedor Nginx/Frontend :3000 (host)
               └─ /api ──► Contenedor Backend :8080 (red interna Docker)
```

**Datos base:**
- Región: `us-east-1`
- Frontend/Nginx en EC2 puerto `3000`
- Backend puerto `8080`, únicamente dentro de la red Docker
- Health check: `GET /api/health` (responde `200` sin autenticación)

---

## Nombres de recursos

| Recurso | Nombre |
|---|---|
| VPC | `web-demo-vpc` |
| Subred pública A | `web-public-a` |
| Subred pública B | `web-public-b` |
| Internet Gateway | `web-demo-igw` |
| Tabla de rutas | `web-public-rt` |
| Security Group ALB | `web-alb-sg` |
| Security Group EC2 | `web-app-sg` |
| Target Group | `web-app-tg` |
| Load Balancer | `web-demo-alb` |
| Launch Template | `web-app-lt` |
| Auto Scaling Group | `web-app-asg` |
| CodeDeploy Application | `web-application` |
| Deployment Group | `web-deployment-group` |

---

## Orden de ejecución recomendado

1. Crear VPC, subredes, Internet Gateway y tabla de rutas.
2. Crear Security Groups (ALB y EC2).
3. Crear el **Target Group** (primero).
4. Crear el **ALB** (segundo).
5. Crear el Launch Template con su User Data.
6. Crear el ASG y asociar el Target Group.
7. Esperar a que la primera EC2 tenga Docker + agente CodeDeploy.
8. Crear/editar el Deployment Group y ejecutar el primer despliegue.
9. Activar health checks de ELB en el ASG.
10. Aumentar `desired capacity` para probar la réplica automática.

> AWS recomienda adjuntar primero el Target Group al ASG y después configurar el
> Deployment Group; hacerlo al revés puede provocar que las instancias sean
> desregistradas inesperadamente.

---

# Parte 0. Requisitos previos: permisos de IAM

Para poder crear los recursos necesitas permisos en la cuenta AWS.
Hay **tres planos distintos** de IAM que conviene no confundir:

1. El **usuario/rol IAM** con el que tú ejecutas la guía (consola o AWS CLI).
2. El **rol de servicio de CodeDeploy** (identidad con la que actúa el servicio).
3. El **rol de perfil de instancia EC2** (identidad de las instancias del ASG).

## 1) Permisos del usuario/rol que ejecuta la guía

Si tu usuario ya es administrador (`AdministratorAccess`) o pertenece a un grupo
de administradores, este apartado no aplica. Para un acceso de **mínimo
privilegio**, adjunta al usuario al menos estas políticas administradas de AWS:

| Área | Política administrada | Para qué sirve |
|---|---|---|
| Red | `AmazonVPCFullAccess` | VPC, subredes, IGW, tablas de rutas |
| Cómputo | `AmazonEC2FullAccess` | Launch Template, instancias, Security Groups |
| Balanceo | `AmazonElasticLoadBalancingFullAccess` | ALB y Target Group |
| Auto Scaling | `AmazonAutoScalingFullAccess` | ASG y sus políticas de escalado |
| Despliegue | `AWSCodeDeployFullAccess` | Application y Deployment Group |

Además, si vas a **crear los roles** desde la consola o a lanzar plantillas que
los referencian, necesitas permisos de IAM (los anteriores no los incluyen):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:GetRole",
        "iam:ListRoles",
        "iam:PutRolePolicy",
        "iam:AttachRolePolicy",
        "iam:CreateInstanceProfile",
        "iam:AddRoleToInstanceProfile",
        "iam:GetInstanceProfile",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
```

> `iam:PassRole` es imprescindible: cuando el Launch Template referencia un
> Instance Profile o el Deployment Group referencia el rol de CodeDeploy, AWS
> exige que tu usuario tenga permiso para "pasar" ese rol.

Si además guardas las revisiones de CodeDeploy en S3 (o las subes con la CLI),
agrega permisos sobre el bucket: `s3:PutObject`, `s3:GetObject`, `s3:ListBucket`
(equivalentes a `AmazonS3FullAccess` limitada al bucket de artefactos).

## 2) Rol de servicio de CodeDeploy

**Ruta:** `IAM → Roles → Create role → Trusted entity type: AWS service → CodeDeploy`

No es un permiso de tu usuario: es la identidad con la que **el propio servicio**
opera sobre tus recursos durante el despliegue.

- Política administrada recomendada: `AWSCodeDeployRole`

Ese rol permite a CodeDeploy (despliegue In-place + ASG + ALB), entre otras cosas:

- `ec2:DescribeInstances`, `ec2:DescribeInstanceStatus`
- `autoscaling:EnterStandby`, `autoscaling:CompleteLifecycleAction`
- `elasticloadbalancing:DescribeTargetGroups`, `elasticloadbalancing:RegisterTargets`, `elasticloadbalancing:DeregisterTargets`
- `codedeploy:*`

> Es el rol que seleccionas en el campo **"Service role"** del Deployment Group.

## 3) Rol de perfil de instancia EC2 (Instance Profile)

**Ruta:** `IAM → Roles → Create role → Trusted entity type: AWS service → EC2`

Es la identidad de las EC2 lanzadas por el ASG. Se asigna en el Launch Template
(campo **IAM Instance Profile**). Políticas según lo que hagan las instancias:

| Política | Motivo |
|---|---|
| `AmazonEC2ContainerRegistryReadOnly` | Si la app se publica en ECR (necesario para `docker pull` de imágenes privadas) |
| `AmazonS3ReadOnlyAccess` | Si el agente de CodeDeploy descarga el bundle desde un bucket S3 privado |
| `CloudWatchAgentServerPolicy` | Si usas `user-data-ec2-cloudwatch.sh` (config en SSM Parameter Store + métricas) |
| `AmazonSSMManagedInstanceCore` | Opcional: acceso por Session Manager para depurar |

> El agente de CodeDeploy lo instala el User Data, pero **la instancia necesita
> permisos para acceder a los artefactos** del despliegue. Con revisiones en S3
> público o GitHub no hace falta permiso extra; con buckets privados o ECR sí.

**Resumen de dónde se usa cada rol:**

| Plano | Rol | Se referencia en |
|---|---|---|
| Usuario IAM | El tuyo (con las políticas anteriores) | Toda la guía |
| Servicio CodeDeploy | Rol de servicio → `AWSCodeDeployRole` | Deployment Group → "Service role" |
| Instancia EC2 | Instance Profile → ECR/S3/CloudWatch | Launch Template → "IAM Instance Profile" |

---

# Parte I. Red

## Paso 1. Crear la VPC

**Ruta:** `VPC → Your VPCs → Create VPC`

| Campo | Valor |
|---|---|
| Resources to create | VPC only |
| Name | `web-demo-vpc` |
| IPv4 CIDR | `10.0.0.0/16` |
| IPv6 | No IPv6 |
| Tenancy | Default |

Después de crearla, activa el DNS:

```
VPC → Your VPCs
  1. Marca la casilla de web-demo-vpc
  2. Actions → Edit VPC settings
  3. Marca las casillas:
       ☑ Enable DNS resolution
       ☑ Enable DNS hostnames
  4. Save
```

- DNS resolution: **Enabled**
- DNS hostnames: **Enabled**

> El diálogo **Edit VPC settings** es el único lugar donde se activan; al crear
> una VPC "VPC only" el DNS hostnames suele quedar deshabilitado. Con estas dos
> opciones activas, las instancias con IP pública reciben su DNS público y el
> resolver de la VPC funciona (lo usa el ALB y CodeDeploy).

Equivalente con AWS CLI:

```bash
aws ec2 modify-vpc-attribute \
  --vpc-id vpc-0xxxxxxxxxxxx \
  --enable-dns-support "{\"Value\":true}"

aws ec2 modify-vpc-attribute \
  --vpc-id vpc-0xxxxxxxxxxxx \
  --enable-dns-hostnames "{\"Value\":true}"
```

## Paso 2. Crear las dos subredes públicas

**Ruta:** `VPC → Subnets → Create subnet`

| Nombre | Zona | CIDR |
|---|---|---|
| `web-public-a` | us-east-1a | `10.0.1.0/24` |
| `web-public-b` | us-east-1b | `10.0.2.0/24` |

Para cada subnet:

```
Seleccionar subnet → Actions → Edit subnet settings
```

Activa:

- **Enable auto-assign public IPv4 address**

> Es necesario porque no se usa NAT Gateway. Las EC2 necesitan una IPv4 pública
> para descargar paquetes, el agente de CodeDeploy y las imágenes.
> El ALB requiere subredes en al menos dos zonas (≥/27 recomendadas; /24 es suficiente).

## Paso 3. Crear y conectar el Internet Gateway

**Ruta:** `VPC → Internet gateways → Create internet gateway`

- Name: `web-demo-igw`

Después:

```
Actions → Attach to a VPC
VPC: web-demo-vpc
```

## Paso 4. Crear la tabla de rutas pública

**Ruta:** `VPC → Route tables → Create route table`

| Campo | Valor |
|---|---|
| Name | `web-public-rt` |
| VPC | `web-demo-vpc` |

Rutas (la `local` ya existe):

| Destino | Target |
|---|---|
| `10.0.0.0/16` | local |
| `0.0.0.0/0` | `web-demo-igw` |

En **Subnet associations**, asocia:

- `web-public-a`
- `web-public-b`

No se necesitan subredes privadas, NAT Gateway ni más tablas de rutas.
La Network ACL predeterminada puede permanecer permitiendo todo el tráfico.

**Verificación:** ambas subredes aparecen asociadas y la ruta `0.0.0.0/0` apunta al IGW.

---

# Parte II. Security Groups

## Paso 5. Security Group del ALB: `web-alb-sg`

**Ruta:** `EC2 → Network & Security → Security Groups → Create security group`
(también disponible en `VPC → Security Groups`; es la misma pantalla)

| Campo | Valor |
|---|---|
| Security group name | `web-alb-sg` |
| Description | SG del ALB web-demo-alb |
| VPC | `web-demo-vpc` |

Entradas (inbound):

| Tipo | Puerto | Origen |
|---|---|---|
| HTTP | 80 | `0.0.0.0/0` |

Salidas (outbound), simplificado:

| Tipo | Destino |
|---|---|
| All traffic | `0.0.0.0/0` |

> Opcional: restringir después la salida al puerto 3000 hacia `web-app-sg`.

> Un SG nuevo **no trae reglas de entrada** (todo denegado), por eso hay que
> añadir el HTTP 80. La regla de salida *All traffic* ya viene creada por
> defecto al crear el SG, así que en outbound normalmente no hay que hacer nada.

Equivalente con AWS CLI:

```bash
# Crear el SG dentro de la VPC
aws ec2 create-security-group \
  --group-name web-alb-sg \
  --description "SG del ALB web-demo-alb" \
  --vpc-id vpc-0xxxxxxxxxxxx

# Regla de entrada: HTTP 80 desde Internet
aws ec2 authorize-security-group-ingress \
  --group-id sg-0xxxxxxxxxxxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0
```

## Paso 6. Security Group de las EC2: `web-app-sg`

**Ruta:** `EC2 → Network & Security → Security Groups → Create security group`
(misma pantalla que el Paso 5)

| Campo | Valor |
|---|---|
| Security group name | `web-app-sg` |
| Description | SG de las EC2 del ASG web-app-asg |
| VPC | `web-demo-vpc` |

Entradas (inbound):

| Tipo | Puerto | Origen |
|---|---|---|
| Custom TCP | 3000 | `web-alb-sg` (buscar el nombre y seleccionarlo → se usa su **ID** como origen) |
| SSH (opcional) | 22 | Tu IP pública `/32` (la IP desde la que harás SSH; en la consola usa el botón **My IP**) |

> **¿Qué IP es "tu IP pública"?** Es la IP pública de tu ordenador —la de tu
> casa/oficina desde donde ejecutarás `ssh`—. **No** es la IP de la EC2 ni la del
> ALB: esa regla define el **origen** del tráfico, no el destino. Para conocerla,
> usa el botón *My IP* al crear la regla o `curl ifconfig.me`. El sufijo `/32`
> indica una sola IP. Si tu IP es dinámica o cambias de red, deberás actualizar
> esta regla. Es **opcional**: sin ella puedes depurar vía SSM Session Manager.

Salidas (outbound):

| Tipo | Destino |
|---|---|
| All traffic | `0.0.0.0/0` |

**No abras:**

- Puerto 3000 desde `0.0.0.0/0`.
- Puerto 80 de la EC2 (pertenece al ALB).
- Puerto interno del backend.

> El puerto público 80 es del ALB. El puerto de destino en las EC2 es el 3000.

> **Por qué el origen es el SG del ALB y no una IP:** el tráfico del ALB hacia
> las EC2 viene de sus ENIs, que llevan asociado `web-alb-sg`. Referenciarlo como
> origen permite ese tráfico **sin abrir el 3000 a internet** (`0.0.0.0/0`).
> Ambos SGs deben pertenecer a la misma VPC (`web-demo-vpc`).
> La regla de salida *All traffic* ya viene por defecto al crear el SG.

Equivalente con AWS CLI:

```bash
# Crear el SG dentro de la VPC
aws ec2 create-security-group \
  --group-name web-app-sg \
  --description "SG de las EC2 del ASG web-app-asg" \
  --vpc-id vpc-0xxxxxxxxxxxx

# Regla de entrada: puerto 3000 permitido SOLO desde el SG del ALB
aws ec2 authorize-security-group-ingress \
  --group-id sg-0xxxxxxxxxxxx \
  --protocol tcp \
  --port 3000 \
  --source-group sg-0xxxxxxxxxxxx   # <-- ID del web-alb-sg

# Regla opcional: SSH desde tu IP pública
aws ec2 authorize-security-group-ingress \
  --group-id sg-0xxxxxxxxxxxx \
  --protocol tcp \
  --port 22 \
  --cidr TU-IP-PUBLICA/32
```

---

# Parte III. Target Group y Load Balancer

## Paso 7. Crear el Target Group (primero)

**Ruta:** `EC2 → Target Groups → Create target group`

En la **primera pantalla** del asistente, apartado *Basic configuration →
Choose a target type* (en español: *Configuración → Elija un tipo de destino*),
selecciona:

| Opción a elegir |
|---|
| **Instances** |

> Esta elección **no se puede modificar después** de crear el Target Group.
> Se elige **Instances** — y no *IP addresses* — porque el ASG registra las EC2
> por su **ID de instancia** y el ALB dirigirá el tráfico a esas instancias.
> *IP addresses* se usa cuando los destinos se registran por IP privada
> (p. ej. on-premise o servicios ajenos al ASG); *Lambda function* y
> *Application Load Balancer* no aplican a este escenario de EC2.

| Campo | Valor |
|---|---|
| Target type | Instances |
| Name | `web-app-tg` |
| Protocol | HTTP |
| Port | 3000 |
| IP address type | IPv4 |
| VPC | `web-demo-vpc` |
| Protocol version | HTTP1 |

Health check:

| Campo | Valor |
|---|---|
| Protocol | HTTP |
| Port | Traffic port |
| Path | `/api/health` |
| Success codes | 200 |
| Interval | 30 segundos |
| Timeout | 5 segundos |
| Healthy threshold | 2 |
| Unhealthy threshold | 2 |

> **No registrar instancias manualmente.** El ASG hará el registro.
> `GET /api/health` debe responder `200` sin autenticación. Idealmente Nginx la
> reenvía al backend, validando Nginx + red Docker + API.

## Paso 8. Crear el Application Load Balancer (segundo)

**Ruta:** `EC2 → Load Balancers → Create Load Balancer → Application Load Balancer`

| Campo | Valor |
|---|---|
| Name | `web-demo-alb` |
| Scheme | Internet-facing |
| IP address type | IPv4 |
| VPC | `web-demo-vpc` |
| Availability Zones | us-east-1a, us-east-1b |
| Subnets | `web-public-a`, `web-public-b` |
| Security Group | `web-alb-sg` |

Listener:

| Protocolo | Puerto | Acción |
|---|---|---|
| HTTP | 80 | Forward to `web-app-tg` |

El ALB expondrá un DNS similar a:

```
web-demo-alb-<id>.us-east-1.elb.amazonaws.com
```

**Verificación:** listener HTTP:80 configurado con forward al Target Group.

---

# Parte IV. Launch Template y User Data

## Paso 9. Crear el Launch Template

**Ruta:** `EC2 → Launch Templates → Create launch template`

> El asistente es una **única página con secciones** que se completan de arriba
> a abajo. A continuación, el orden real de esas secciones.

### 9.1 Sección: Launch template name and description

| Campo | Valor |
|---|---|
| Launch template name | `web-app-lt` |
| Auto Scaling guidance | Marca la casilla *Provide guidance to help me set up a template that I can use with EC2 Auto Scaling* |

### 9.2 Sección: Application and OS images (AMI)

- Ve a la pestaña **Browse more AMIs** (Ubuntu normalmente no está en *Quick Start*).
- Busca: `ubuntu-noble-24.04` (o el patrón `ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*`).
- Selecciona una AMI **Ubuntu Server 24.04 LTS** de arquitectura `x86_64`/`amd64`.

### 9.3 Sección: Instance type

| Campo | Valor |
|---|---|
| Instance type | `t3.small` (recomendado) |

> `t3.micro` puede funcionar, pero dos contenedores + Docker + CodeDeploy +
> sistema operativo pueden quedarse sin memoria. Para la práctica usar `t3.small`.

### 9.4 Sección: Key pair (login)

- **Opcional.** Si tienes un key pair para conectarte por SSH, selecciónalo.
- Si no tienes uno: elige **Proceed without a key pair**.

### 9.5 Sección: Network settings → Configuración de red (una sola interfaz)

Aquí se define la **única interfaz de red** de las instancias. En la tarjeta de
interfaz que aparece por defecto (device index 0), configura:

| Campo dentro de la tarjeta | Valor |
|---|---|
| Network interface | New interface |
| Device index | 0 |
| Subnet | **Don't include in launch template** |
| Auto-assign public IP | **Enable** |
| Security Group | `web-app-sg` (búscalo y selecciónalo) |
| Delete on termination | ✅ casilla marcada |
| IPv6 | No agregar / no incluir |

> - No seleccionar subnet en el Launch Template: las subredes se eligen en el ASG.
> - No usar interfaz de red existente: cada EC2 necesita una interfaz nueva.
> - *Auto-assign public IP* puede verse como un menú (*Enable* / *Disable* /
>   *Use subnet setting*): elige **Enable**.

### 9.6 Sección: Storage (volumes) → aquí se configura el disco

| Campo | Valor |
|---|---|
| Volume 1 (volumen raíz) → Size | `15` o `20` GiB |
| Volume 1 → Volume type | `gp3` |

> AWS pone por defecto el volumen raíz con **8 GiB gp3**. Cámbiale el **tamaño a
> 15–20 GiB** y deja el tipo **gp3**. La casilla *Delete on termination* ya viene
> marcada por defecto en el volumen raíz.

### 9.7 Sección: Advanced details (Configuración avanzada)

1. **IAM instance profile**: selecciona el perfil de instancia de tu práctica
   (p. ej. `EC2-CodeDeploy-Role`).
2. Desplázate hasta el final de *Advanced details* y localiza el campo
   **User data**:
   - Formato: **As text**.
   - Pega el contenido del **Paso 10** (User Data).
3. Deja el resto de opciones avanzadas por defecto y pulsa **Create launch
   template**.

## Paso 10. User Data

El User Data **solo prepara la instancia**: no despliega la aplicación, esa
responsabilidad es de CodeDeploy.

```bash
#!/bin/bash
set -euxo pipefail
export DEBIAN_FRONTEND=noninteractive

AWS_REGION="us-east-1"

apt-get update
apt-get install -y \
  ca-certificates \
  curl \
  gnupg \
  wget \
  unzip

curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
sh /tmp/get-docker.sh
systemctl enable --now docker
usermod -aG docker ubuntu

ARCHITECTURE="$(uname -m)"
curl -fsSL \
  "https://awscli.amazonaws.com/awscli-exe-linux-${ARCHITECTURE}.zip" \
  -o /tmp/awscliv2.zip
unzip -q /tmp/awscliv2.zip -d /tmp
/tmp/aws/install

wget -q \
  -O /tmp/codedeploy-install \
  "https://aws-codedeploy-${AWS_REGION}.s3.${AWS_REGION}.amazonaws.com/latestv2/install"
chmod +x /tmp/codedeploy-install
/tmp/codedeploy-install auto
systemctl enable --now codedeploy-agent

docker --version
docker compose version
aws --version
systemctl status codedeploy-agent --no-pager
```

> La URL debe usar **`latestv2/install`** (agente CodeDeploy 2.x, binario
> autocontenido, sin Ruby). El instalador `latest/install` es el antiguo y causa
> el error de dependencia de Ruby.

Logs de arranque en:

```
/var/log/cloud-init-output.log
```

**Verificación:** Docker activo, AWS CLI instalada, agente `codedeploy-agent` en `active (running)`.

---

# Parte V. Auto Scaling Group

## Paso 11. Crear el ASG

**Ruta:** `EC2 → Auto Scaling Groups → Create Auto Scaling group`

| Campo | Valor |
|---|---|
| Name | `web-app-asg` |
| Launch Template | `web-app-lt` |
| Launch Template version | Específica o Default |
| VPC | `web-demo-vpc` |
| Subnets | `web-public-a`, `web-public-b` |
| Purchase option | On-Demand |
| Load balancing | Attach to existing load balancer |
| Target Group | `web-app-tg` |

> No se adjunta el ALB directamente: **se adjunta el Target Group**.

### Capacidad inicial (primer despliegue)

| Capacidad | Valor |
|---|---|
| Minimum | 1 |
| Desired | 1 |
| Maximum | 4 |

### Capacidad final (tras el primer despliegue exitoso)

| Capacidad | Valor |
|---|---|
| Minimum | 2 |
| Desired | 2 |
| Maximum | 4 |

> Esto permite comprobar que una segunda instancia creada por el ASG recibe
> automáticamente la última revisión de CodeDeploy.

### Health checks durante la creación

- Health check type: `EC2`
- Health check grace period: `600 seconds`

> La primera instancia todavía no tiene la aplicación. Si se activa de inmediato
> el health check del ALB, el ASG podría reemplazarla por no responder en 3000.

Después del primer despliegue exitoso, **editar el ASG**:

```
Health checks:
  EC2: Enabled
  ELB: Enabled

Health check grace period:
  300–600 seconds
```

### Política de escalamiento (Target Tracking)
Elegir opción Política de escalado de seguimiento de destino
| Campo | Valor |
|---|---|
| Metric type | Average CPU utilization |
| Target value | 60 |
| Instance warmup | 300 segundos |

### Tags (propagar a las instancias)

| Key | Value |
|---|---|
| Name | `web-app-asg-instance` |
| Application | `web-application` |
| Environment | `demo` |

**Verificación:** una EC2 lanzada en el ASG, registrada en `web-app-tg`,
con Docker y agente CodeDeploy activos.

---

# Parte VI. CodeDeploy

## Paso 12. Configurar el Deployment Group

### 12.0 Requisito previo: crear la CodeDeploy Application `web-application`

El Deployment Group **vive dentro de una aplicación** de CodeDeploy. Si aún no tienes la aplicación (o no la encuentras), créala primero:

1. Busca y abre el servicio **CodeDeploy** (barra de búsqueda de la consola).
2. En el menú izquierdo, elige **Applications**.
3. Pulsa **Create application**.
4. Configura:

   | Campo | Valor |
   |---|---|
   | Application name | `web-application` |
   | Compute platform | **EC2/On-premises** |

5. Pulsa **Create application**.

> Si la aplicación no existe, no verás la ruta `web-application → Create
> deployment group` que indica la guía: primero debe existir `web-application`.

### 12.1 Crear el Deployment Group

1. En **CodeDeploy → Applications**, haz clic sobre el nombre `web-application`.
2. En la página de la aplicación, abre la pestaña **Deployment groups**.
3. Pulsa **Create deployment group**.

Se abre un formulario. Completa cada sección en orden:

#### Deployment group name
| Campo | Valor |
|---|---|
| Deployment group name | `web-deployment-group` |
| Service role | `EC2-CodeDeploy-Role` (búscalo en el desplegable de roles) |

#### Deployment type
| Campo | Valor |
|---|---|
| Deployment type | **In-place** |

#### Environment configuration
| Campo | Valor |
|---|---|
| Environment configuration | **Amazon EC2 Auto Scaling groups** |
| Auto Scaling groups | Selecciona `web-app-asg` |

> (Opcional, aparece aquí) **Add a termination hook to Auto Scaling groups**:
> dejarlo desmarcado para esta demo.

> **Nota — Agent configuration with Systems Manager:** esta opción **solo
> aparece** cuando en *Environment configuration* eliges **Amazon EC2 instances**
> u **On-premises instances** (por tags). Al usar **Amazon EC2 Auto Scaling
> groups**, CodeDeploy no la muestra, porque el agente se instala a través de la
> AMI/User Data del Launch Template. Como tu User Data ya instala el agente, no
> hay nada que configurar aquí.

#### Deployment configuration
| Campo | Valor |
|---|---|
| Deployment configuration | `CodeDeployDefault.OneAtATime` |

#### Load balancer
| Campo | Valor |
|---|---|
| Enable load balancing | ✅ marcado |
| Application Load Balancer target groups | Selecciona **`web-app-tg`** de la lista |

> En la consola actual esta sección se llama **Load balancer** y va después de
> *Deployment configuration*. Al marcar *Enable load balancing* aparecen listas
> de Classic Load Balancers, **Application Load Balancer target groups** y Network
> Load Balancer target groups: ahí eliges `web-app-tg`. No es un campo de texto
> que se escriba; es una lista donde se selecciona el Target Group del ALB.

#### Advanced → Automatic rollback
| Campo | Valor |
|---|---|
| Roll back when a deployment fails | ✅ activado |

Pulsa **Create deployment group** para terminar.

> Si el Deployment Group ya existe, edítalo en la misma pestaña
> **Deployment groups** con el botón **Edit** en lugar de crearlo.

Con **Load balancing** activado, CodeDeploy realiza automáticamente:

1. Retira temporalmente la instancia del Target Group.
2. Ejecuta el despliegue.
3. Valida la aplicación.
4. Registra nuevamente la instancia.
5. Espera a que quede saludable.

> No se necesitan scripts para registrar/desregistrar las EC2.

Equivalente con AWS CLI (opcional):

```bash
# Crear la aplicación (solo la primera vez)
aws deploy create-application \
  --application-name web-application \
  --compute-platform Server

# Crear el Deployment Group
aws deploy create-deployment-group \
  --application-name web-application \
  --deployment-group-name web-deployment-group \
  --service-role-arn arn:aws:iam::<CUENTA>:role/EC2-CodeDeploy-Role \
  --deployment-style '{"deploymentType":"IN_PLACE","deploymentOption":"WITHOUT_TRAFFIC_CONTROL"}' \
  --auto-scaling-groups web-app-asg \
  --deployment-config-name CodeDeployDefault.OneAtATime \
  --load-balancer-info '{"targetGroupInfoList":[{"name":"web-app-tg"}]}'
```

### Termination hook

Para la demostración dejarlo **desactivado**:

```
Add a termination hook to Auto Scaling groups
```

> Evitar asociar varios Deployment Groups al mismo ASG: los despliegues y
> lifecycle hooks pueden interferirse.

## Paso 13. Primer despliegue y validación final

1. `Create deployment` sobre `web-deployment-group`.
2. Esperar a que la primera EC2 reciba la aplicación.
3. Abrir en el navegador:
   - `http://<DNS-ALB>/` → frontend.
   - `http://<DNS-ALB>/api/health` → `200 OK`.
4. Editar el ASG: activar `ELB health check` y ajustar grace period.
5. Subir `Desired capacity` a 2 y comprobar que la nueva instancia recibe sola
   la última revisión de CodeDeploy.
6. Probar la política de escalado subiendo la CPU y observando que el ASG lanza
   nuevas instancias (máx. 4).

---

# Checklist de verificación

**IAM (Parte 0)**
- [ ] Usuario IAM con permisos de VPC/EC2/ELB/ASG/CodeDeploy (+ `iam:PassRole`).
- [ ] Rol de servicio de CodeDeploy con `AWSCodeDeployRole`.
- [ ] Rol de Instance Profile EC2 con ECR/S3/CloudWatch, asignado al Launch Template.

**Infraestructura**
- [ ] VPC `10.0.0.0/16` con DNS habilitado.
- [ ] Subredes públicas en 2 AZ con auto-assign public IP.
- [ ] IGW conectado y ruta `0.0.0.0/0` en la tabla pública.
- [ ] SGs: ALB (80/0.0.0.0/0) y EC2 (3000/`web-alb-sg`).
- [ ] Target Group HTTP:3000 con health check `/api/health`.
- [ ] ALB internet-facing HTTP:80 → forward a `web-app-tg`.
- [ ] Launch Template con User Data (Docker + AWS CLI + agente CodeDeploy v2).
- [ ] ASG 2/2/4 asociado a `web-app-tg`, con health checks EC2+ELB.
- [ ] Deployment Group con load balancing sobre `web-app-asg`.
- [ ] Primer despliegue exitoso y réplica automática verificada.
