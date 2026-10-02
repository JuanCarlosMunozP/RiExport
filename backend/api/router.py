from fastapi import APIRouter
from sqlalchemy import text

from auth.router import router as auth_router
from core.config import settings
from core.errors import APIError
from customers.router import router as customers_router
from database.session import get_engine
from documents.router import router as documents_router
from exports.router import router as exports_router
from farms.router import router as farms_router
from inventory.router import router as inventory_router
from jobs.router import router as jobs_router
from logistics.router import router as logistics_router
from notifications.router import router as notifications_router
from orders.router import router as orders_router
from payments.router import router as payments_router
from products.router import router as products_router
from reports.router import router as reports_router
from roles.router import router as roles_router
from suppliers.router import router as suppliers_router
from users.router import router as users_router

router = APIRouter()
api_v1_router = APIRouter()


@router.get("/health/live", tags=["health"])
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready", tags=["health"])
def readiness() -> dict[str, str]:
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise APIError(
            status_code=503,
            code="SERVICE_UNAVAILABLE",
            message="El servicio no está disponible temporalmente.",
        ) from exc
    return {"status": "ready"}


for module_router in (
    auth_router,
    users_router,
    roles_router,
    products_router,
    suppliers_router,
    farms_router,
    customers_router,
    orders_router,
    exports_router,
    documents_router,
    inventory_router,
    payments_router,
    logistics_router,
    notifications_router,
    reports_router,
    jobs_router,
):
    api_v1_router.include_router(module_router)

router.include_router(api_v1_router, prefix=settings.api_v1_prefix)
