# RiExport API

Backend FastAPI para la plataforma RiExport. La documentación funcional y de arquitectura vive en el proyecto de documentación `D:\plataforma_exportacion_cafe_cacao\docs`.

## Preparar el entorno (PowerShell)

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
uv sync --locked --active --all-groups
Copy-Item .env.example .env
```

El archivo `.python-version` fija el intérprete de referencia y `uv.lock` fija las versiones directas y transitivas. Instala `uv` una vez en el equipo antes de sincronizar. Usa `uv lock` solo cuando cambien las dependencias; revisa y conserva el `uv.lock` actualizado junto con `pyproject.toml`.

Copia `.env.example` como `.env` y define las variables adecuadas para el entorno. `.env` no se versiona.

`APP_ENV` acepta `development`, `testing` o `production`. En desarrollo se activa el modo debug; Swagger y ReDoc solo se habilitan fuera de producción. El nivel de logs se controla con `LOG_LEVEL`. Configura `DATABASE_URL` con el formato `postgresql+psycopg://usuario:clave@host:5432/base`. SQLAlchemy usa conexiones síncronas con `psycopg`, comprobación de conexiones del pool y sesiones por petición. `/health/ready` comprueba que PostgreSQL acepte una consulta; no crea la base ni sus tablas.

Para Flutter Web, `CORS_ORIGINS` es una lista de orígenes separados por coma, sin rutas, por ejemplo `https://app.example.com`. En desarrollo se aceptan automáticamente orígenes HTTP/HTTPS de `localhost` y `127.0.0.1` en cualquier puerto; producción no usa esa excepción. Las peticiones Bearer no necesitan cookies, por lo que `CORS_ALLOW_CREDENTIALS` queda desactivado por defecto. Flutter para Android/iOS no aplica CORS.

Para ejecutar con otro perfil en PowerShell, establece `APP_ENV` antes de iniciar:

```powershell
$env:APP_ENV = "testing"
.\run.ps1
```

## Ejecutar

Desde `D:\riexport\backend`:

```powershell
.\run.ps1
```

El backend usa siempre el puerto `8001`: OpenAPI/Swagger está en `http://127.0.0.1:8001/docs` en `development` y `testing`; en `production` la documentación interactiva y el esquema OpenAPI quedan deshabilitados. El estado de vida está en `/health/live` y la disponibilidad de base de datos en `/health/ready`.

Los routers de dominio están registrados bajo `/api/v1`. Autenticación,
administración de usuarios y roles exponen las operaciones implementadas hasta
el momento; las demás operaciones de negocio se incorporarán por actividad.

## Hash de contraseñas

`core.security.hash_password` genera hashes bcrypt con salt aleatorio y costo
12; `verify_password` compara credenciales sin revelar hashes inválidos. Las
contraseñas se limitan a 72 bytes UTF-8, el máximo admitido por bcrypt, y se
rechazan bytes nulos.

El mismo módulo expone `create_access_token` y `decode_access_token`. Los JWT
usan HS256, requieren `sub`, `iat`, `exp`, `iss`, `jti` y `token_use=access`, y
no incluyen roles ni permisos. Configura `JWT_SECRET_KEY` con al menos 32 bytes
aleatorios (por ejemplo, genera uno con
`python -c "import secrets; print(secrets.token_urlsafe(48))"`). El vencimiento
por defecto es 30 minutos y se ajusta con `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`; es
un valor inicial pendiente de aprobación. Un secreto ausente o débil bloquea
la emisión de tokens.

`POST /api/v1/auth/login` recibe `email` y `password`, verifica la contraseña,
rechaza de forma uniforme credenciales incorrectas y cuentas inactivas, y
responde con `access_token`, `token_type` y `expires_in`. Las rutas protegidas
inyectan `CurrentUser`, que valida el Bearer JWT y vuelve a comprobar en la base
que la cuenta siga activa. `require_permission` aplica los permisos asignados al
rol activo en cada solicitud.

`POST /api/v1/auth/password-reset/request` recibe `email` y crea una solicitud
de recuperación con token de un solo uso, almacenando únicamente su hash y con
vencimiento de 30 minutos. La respuesta no revela si la cuenta existe. El envío
del enlace requiere integrar y configurar un proveedor de correo.

## Versionado de base de datos

Alembic carga `DATABASE_URL` desde `.env`, usa `database.base.Base.metadata` e importa `database.models`, el registro de todos los modelos ORM de dominio, para detectar entidades al autogenerar revisiones:

```powershell
alembic revision --autogenerate -m "descripcion_del_cambio"
alembic upgrade head
```

Consulta la revisión aplicada con `alembic current`, el historial con `alembic history` y revierte una revisión con `alembic downgrade -1`. Revisa siempre la migración generada antes de aplicarla. El modelo ORM inicial refleja `docs/modelo-datos.md`; las reglas transaccionales que cruzan varias tablas permanecen en servicios y no se simulan como constraints simples.

## Datos semilla

El script `scripts.seed_data` inserta las unidades `kg` y `t`, certificaciones,
roles y el catálogo de permisos implementado. También asigna al rol
`administrador` los permisos de gestión de usuarios y roles. Puede ejecutarse
más de una vez: inserta claves faltantes y conserva asignaciones existentes.
Para cargar solo roles y permisos:

```powershell
.\venv\Scripts\python.exe -m scripts.seed_data --roles-only
```

El script requiere `DATABASE_URL` y no crea usuarios. El rol `cliente` se
registra como catálogo, pero su aislamiento para consultar solo envíos propios
debe implementarse antes de habilitar acceso externo. Países y monedas aún
requieren definición.
