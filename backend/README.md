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

Los routers de dominio están registrados bajo `/api/v1`; todavía no exponen operaciones de negocio. Los modelos, servicios y repositorios se implementarán por actividad siguiendo el contrato REST documentado.

## Versionado de base de datos

Alembic carga `DATABASE_URL` desde `.env`, usa `database.base.Base.metadata` e importa `database.models`, el registro de todos los modelos ORM de dominio, para detectar entidades al autogenerar revisiones:

```powershell
alembic revision --autogenerate -m "descripcion_del_cambio"
alembic upgrade head
```

Consulta la revisión aplicada con `alembic current`, el historial con `alembic history` y revierte una revisión con `alembic downgrade -1`. Revisa siempre la migración generada antes de aplicarla. El modelo ORM inicial refleja `docs/modelo-datos.md`; las reglas transaccionales que cruzan varias tablas permanecen en servicios y no se simulan como constraints simples.

## Datos semilla

El script `scripts.seed_data` inserta las unidades `kg` y `t` y las
certificaciones base descritas en los requerimientos. Puede ejecutarse más de
una vez: inserta únicamente claves que todavía no existan y conserva los
valores ya presentes.

```powershell
.\venv\Scripts\python.exe -m scripts.seed_data
```

El script requiere `DATABASE_URL` y no crea usuarios ni roles. La matriz de
permisos, los países, las monedas y los nombres definitivos de roles aún deben
aprobarse antes de añadirlos a esta semilla.
