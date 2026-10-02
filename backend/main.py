from fastapi import FastAPI

from api.router import router
from core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API de la plataforma RiExport.",
)
app.include_router(router)
