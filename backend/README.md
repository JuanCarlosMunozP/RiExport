# RiExport API

Backend FastAPI para la plataforma RiExport. La documentación funcional y de arquitectura vive en el proyecto de documentación `D:\plataforma_exportacion_cafe_cacao\docs`.

## Preparar el entorno (PowerShell)

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
Copy-Item .env.example .env
```

Copia `.env.example` como `.env` y define las variables adecuadas para el entorno. `.env` no se versiona.

`APP_ENV` acepta `development`, `testing` o `production`. En desarrollo se activa el modo debug; Swagger y ReDoc solo se habilitan fuera de producción. El nivel de logs se controla con `LOG_LEVEL`. Configura `DATABASE_URL` con el formato `postgresql+psycopg://usuario:clave@host:5432/base`. SQLAlchemy usa conexiones síncronas con `psycopg`, comprobación de conexiones del pool y sesiones por petición. `/health/ready` comprueba que PostgreSQL acepte una consulta; no crea la base ni sus tablas.

Para ejecutar con otro perfil en PowerShell, establece `APP_ENV` antes de iniciar:

```powershell
$env:APP_ENV = "testing"
uvicorn main:app
```

## Ejecutar

Desde `D:\riexport\backend`:

```powershell
uvicorn main:app --reload
```

En `development` y `testing`, OpenAPI/Swagger estará en `http://127.0.0.1:8000/docs`; en `production` la documentación interactiva y el esquema OpenAPI quedan deshabilitados. El estado de vida está en `/health/live` y la disponibilidad de base de datos en `/health/ready`.

Los routers de dominio están registrados bajo `/api/v1`; todavía no exponen operaciones de negocio. Los modelos, servicios y repositorios se implementarán por actividad siguiendo el contrato REST documentado.
