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

Configura `DATABASE_URL` en `.env` con una base PostgreSQL local antes de usar `/health/ready` o implementar módulos que acceden a datos.

## Ejecutar

Desde `D:\riexport\backend`:

```powershell
uvicorn main:app --reload
```

OpenAPI/Swagger estará en `http://127.0.0.1:8000/docs`; el estado de vida en `/health/live` y la disponibilidad de base de datos en `/health/ready`.

Los routers de dominio están registrados bajo `/api/v1`; todavía no exponen operaciones de negocio. Los modelos, servicios y repositorios se implementarán por actividad siguiendo el contrato REST documentado.
