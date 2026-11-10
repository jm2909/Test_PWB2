"""Cross-cutting HTTP middleware: correlation IDs, security headers, global error handlers."""

import re
import uuid

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

CORRELATION_HEADER = "X-Correlation-ID"
_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,96}$")

log = structlog.get_logger("app.http")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        supplied = request.headers.get(CORRELATION_HEADER, "")
        correlation_id = supplied if _SAFE_ID.match(supplied) else uuid.uuid4().hex
        request.state.correlation_id = correlation_id
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
        response = await call_next(request)
        response.headers[CORRELATION_HEADER] = correlation_id
        log.info("request", method=request.method, path=request.url.path, status=response.status_code)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
        response.headers.setdefault("Cache-Control", "no-store")
        return response


def _detail(status_code: int, detail: object, headers: dict[str, str] | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail}, headers=headers)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exc(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _detail(exc.status_code, exc.detail, dict(exc.headers) if exc.headers else None)

    @app.exception_handler(RequestValidationError)
    async def validation_exc(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Only field location and message: never echo submitted values (may hold PII).
        errors = [
            {"loc": [str(p) for p in e.get("loc", ())], "msg": str(e.get("msg", "invalid"))}
            for e in exc.errors()
        ]
        return _detail(422, errors)

    @app.exception_handler(Exception)
    async def unhandled_exc(request: Request, exc: Exception) -> JSONResponse:
        log.error("unhandled_error", error_type=type(exc).__name__, path=request.url.path)
        return _detail(500, "Internal server error")
