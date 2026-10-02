import logging
import re
from collections.abc import Mapping, Sequence
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.responses import ErrorDetail, ErrorPayload, ErrorResponse

logger = logging.getLogger(__name__)
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class APIError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        *,
        details: Sequence[ErrorDetail | Mapping[str, str]] = (),
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = [
            detail
            if isinstance(detail, ErrorDetail)
            else ErrorDetail.model_validate(detail)
            for detail in details
        ]
        self.headers = dict(headers or {})


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", f"req_{uuid4().hex}")


def _error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: Sequence[ErrorDetail] = (),
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    request_id = _request_id(request)
    body = ErrorResponse(
        error=ErrorPayload(
            code=code,
            message=message,
            details=list(details),
            request_id=request_id,
        )
    )
    response_headers = dict(headers or {})
    response_headers["X-Request-ID"] = request_id
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json"),
        headers=response_headers,
    )


async def _handle_api_error(request: Request, exc: APIError) -> JSONResponse:
    return _error_response(
        request,
        exc.status_code,
        exc.code,
        exc.message,
        exc.details,
        exc.headers,
    )


async def _handle_http_error(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    defaults = {
        400: ("BAD_REQUEST", "La solicitud no es válida."),
        401: ("UNAUTHORIZED", "Se requiere autenticación válida."),
        403: ("FORBIDDEN", "No tienes permiso para esta operación."),
        404: ("NOT_FOUND", "El recurso solicitado no existe."),
        405: ("METHOD_NOT_ALLOWED", "El método no está permitido para este recurso."),
        409: ("CONFLICT", "La solicitud entra en conflicto con el estado actual."),
        422: ("VALIDATION_ERROR", "La solicitud contiene datos no válidos."),
        429: ("RATE_LIMIT_EXCEEDED", "Se excedió el límite de solicitudes."),
        503: ("SERVICE_UNAVAILABLE", "El servicio no está disponible temporalmente."),
    }
    fallback = (
        ("INTERNAL_SERVER_ERROR", "Ocurrió un error inesperado.")
        if exc.status_code >= 500
        else ("HTTP_ERROR", "La solicitud no pudo completarse.")
    )
    code, default_message = defaults.get(exc.status_code, fallback)
    message = (
        exc.detail
        if isinstance(exc.detail, str)
        and exc.detail not in {"Not Found", "Method Not Allowed"}
        else default_message
    )
    return _error_response(
        request,
        exc.status_code,
        code,
        message,
        headers=exc.headers,
    )


def _validation_code(error_type: str) -> tuple[str, str]:
    if error_type == "missing":
        return "required", "Este campo es obligatorio."
    if error_type == "extra_forbidden":
        return "unknown_field", "Este campo no está permitido."
    if error_type.endswith(("_parsing", "_type")):
        return "invalid_format", "El formato o tipo del valor no es válido."
    return "invalid_value", "El valor no es válido."


async def _handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details: list[ErrorDetail] = []
    for error in exc.errors():
        location = [
            str(part)
            for part in error.get("loc", ())
            if part not in {"body", "query", "path", "header", "cookie"}
        ]
        code, message = _validation_code(str(error.get("type", "")))
        details.append(
            ErrorDetail(
                field=".".join(location) or None,
                code=code,
                message=message,
            )
        )
    return _error_response(
        request,
        422,
        "VALIDATION_ERROR",
        "La solicitud contiene datos no válidos.",
        details,
    )


async def _handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    request_id = _request_id(request)
    logger.error(
        "Unhandled exception request_id=%s",
        request_id,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return _error_response(
        request,
        500,
        "INTERNAL_SERVER_ERROR",
        "Ocurrió un error inesperado.",
    )


def install_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(APIError, _handle_api_error)
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, _handle_http_error)
    app.add_exception_handler(Exception, _handle_unexpected_error)


def request_id_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        supplied_id = request.headers.get("X-Request-ID", "")
        request_id = (
            supplied_id
            if _REQUEST_ID_PATTERN.fullmatch(supplied_id)
            else f"req_{uuid4().hex}"
        )
        request.state.request_id = request_id
        try:
            response = await call_next(request)
        except Exception as exc:  # noqa: BLE001 - normalize unhandled API failures
            response = await _handle_unexpected_error(request, exc)
        response.headers["X-Request-ID"] = request_id
        return response
