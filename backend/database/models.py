"""Import all domain models so Alembic can inspect complete metadata."""

from importlib import import_module

MODEL_MODULES = (
    "audit",
    "customers",
    "documents",
    "exports",
    "farms",
    "inventory",
    "jobs",
    "logistics",
    "notifications",
    "orders",
    "payments",
    "products",
    "roles",
    "suppliers",
    "users",
)

for module_name in MODEL_MODULES:
    import_module(f"{module_name}.models")
