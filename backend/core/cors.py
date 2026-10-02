from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import Settings


def configure_cors(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Idempotency-Key",
            "X-Request-ID",
        ],
        expose_headers=["Location", "Retry-After", "X-Request-ID"],
        max_age=600,
    )
