"""App factory. Every router is included once, under API_PREFIX, in the loop below."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import API_PREFIX, get_settings
from app.database import SessionLocal
from app.middleware.http import (
    CorrelationIdMiddleware,
    SecurityHeadersMiddleware,
    register_exception_handlers,
)
from app.middleware.logging_config import configure_logging
from app.routers import (
    accounts,
    alerts,
    auth,
    consents,
    dashboard,
    deviation_events,
    device_connections,
    goals,
    insights,
    metric_explanations,
    onboarding,
    recommendations,
    sync,
    trends,
)

# Routers register here as their tasks land (resource paths only; the prefix is added below).
ROUTERS: list[APIRouter] = [
    accounts.router,
    auth.router,
    onboarding.router,
    insights.router,
    consents.router,
    device_connections.router,
    goals.router,
    sync.router,
    dashboard.router,
    trends.router,
    metric_explanations.router,
    deviation_events.router,
    alerts.router,
    recommendations.router,
]

from app.services.deviation_service import post_ingest_hook  # noqa: E402
from app.services.sync_service import register_post_ingest_hook  # noqa: E402

log = structlog.get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    register_post_ingest_hook(post_ingest_hook)  # idempotent; keeps detection active on every app start
    if settings.seed_on_start:
        from app.seeds import run_all

        with SessionLocal() as db:
            run_all(db)
    yield


def create_app() -> FastAPI:
    settings = get_settings()  # fails at startup when JWT_SECRET_KEY is missing
    configure_logging(settings.debug)
    app = FastAPI(
        title="Sapphire FitConnect API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.debug else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Correlation-ID"],
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    register_exception_handlers(app)
    register_post_ingest_hook(post_ingest_hook)  # deviation detection after each sync

    for router in ROUTERS:
        app.include_router(router, prefix=API_PREFIX)

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    def ready() -> dict[str, str]:
        try:
            with SessionLocal() as db:
                db.execute(text("SELECT 1"))
        except Exception as exc:
            log.error("readiness_failed", error_type=type(exc).__name__)
            raise HTTPException(status_code=503, detail="Database unavailable") from exc
        return {"status": "ready"}

    return app


app = create_app()
