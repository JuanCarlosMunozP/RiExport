from fastapi import FastAPI

from api.router import router
from core.config import settings
from core.errors import install_exception_handlers, request_id_middleware
from core.logging import configure_logging

configure_logging(settings.log_level)
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API de la plataforma RiExport.",
    debug=settings.debug,
    docs_url="/docs" if settings.api_docs_enabled else None,
    redoc_url="/redoc" if settings.api_docs_enabled else None,
    openapi_url="/openapi.json" if settings.api_docs_enabled else None,
)
app.include_router(router)
install_exception_handlers(app)
request_id_middleware(app)
