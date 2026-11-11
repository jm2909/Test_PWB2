"""Global exception handlers producing {"detail": ...}."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.errors import DomainError

logger = logging.getLogger("app.errors")


async def _domain(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, DomainError):
        raise exc
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers)


async def _http(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, StarletteHTTPException):
        raise exc
    return JSONResponse(
        {"detail": exc.detail}, status_code=exc.status_code, headers=getattr(exc, "headers", None)
    )


async def _validation(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        raise exc
    # Never echo submitted input (may contain passwords or health values).
    errors = [
        {"loc": list(e.get("loc", [])), "msg": e.get("msg", ""), "type": e.get("type", "")}
        for e in exc.errors()
    ]
    return JSONResponse({"detail": errors}, status_code=422)


async def _value(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"detail": "Request could not be processed"}, status_code=400)


async def _unexpected(_: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled %s", type(exc).__name__, exc_info=exc)
    return JSONResponse({"detail": "An unexpected error occurred"}, status_code=500)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _domain)
    app.add_exception_handler(StarletteHTTPException, _http)
    app.add_exception_handler(RequestValidationError, _validation)
    app.add_exception_handler(ValueError, _value)
    app.add_exception_handler(Exception, _unexpected)
