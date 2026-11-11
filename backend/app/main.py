"""Application factory."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import text

from app import database
from app.config import get_settings
from app.logging_config import configure_logging
from app.middleware.errors import register_exception_handlers
from app.middleware.http import RequestMiddleware
from app.observability import metrics, setup_tracing
from app.routers import alerts as alerts_router
from app.routers import auth as auth_router
from app.routers import connections as connections_router
from app.routers import consents as consents_router
from app.routers import dashboard as dashboard_router
from app.routers import data_rights as data_rights_router
from app.routers import goals as goals_router
from app.routers import insights as insights_router
from app.routers import readings as readings_router
from app.routers import support as support_router
from app.routers import trends as trends_router
from app.services.alert import register_alert_evaluation

API_PREFIX = "/api/v1"
logger = logging.getLogger("app")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.debug)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if settings.seed_on_startup:
            from app.seed import run_seed

            run_seed()
        yield

    app = FastAPI(
        title="Sapphire FitConnect API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Correlation-ID"],
        expose_headers=["X-Correlation-ID"],
    )
    app.add_middleware(RequestMiddleware)  # added last = outermost
    register_exception_handlers(app)

    @app.get("/health", tags=["Operations"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["Operations"])
    def ready() -> JSONResponse:
        try:
            with database.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:  # noqa: BLE001
            return JSONResponse({"detail": "Database is not ready"}, status_code=503)
        return JSONResponse({"status": "ready"})

    @app.get("/metrics", include_in_schema=False)
    def metrics_endpoint() -> PlainTextResponse:
        return PlainTextResponse(metrics.render())

    # Every router is mounted here, once, under the API prefix.
    app.include_router(auth_router.router, prefix=API_PREFIX)
    app.include_router(consents_router.router, prefix=API_PREFIX)
    app.include_router(dashboard_router.router, prefix=API_PREFIX)
    app.include_router(data_rights_router.router, prefix=API_PREFIX)
    app.include_router(connections_router.router, prefix=API_PREFIX)
    app.include_router(readings_router.router, prefix=API_PREFIX)
    app.include_router(trends_router.router, prefix=API_PREFIX)
    app.include_router(insights_router.router, prefix=API_PREFIX)
    app.include_router(alerts_router.router, prefix=API_PREFIX)
    app.include_router(goals_router.router, prefix=API_PREFIX)
    app.include_router(support_router.router, prefix=API_PREFIX)
    register_alert_evaluation()

    setup_tracing(app, database.engine)
    return app


app = create_app()
