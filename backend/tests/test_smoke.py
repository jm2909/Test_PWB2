import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect

from app.config import API_PREFIX
from app.database import Base
from app.main import app, create_app

BACKEND = Path(__file__).resolve().parents[1]


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_checks_database(client: TestClient) -> None:
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_security_and_correlation_headers(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Correlation-ID": "abc-123"})
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "Strict-Transport-Security" in response.headers
    assert response.headers["X-Correlation-ID"] == "abc-123"


def test_unknown_route_uses_detail_shape(client: TestClient) -> None:
    response = client.get("/nope")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_migration_to_head_builds_every_model_table() -> None:
    import os

    with tempfile.TemporaryDirectory() as tmp:
        url = f"sqlite:///{Path(tmp, 'migrated.db').as_posix()}"
        env = {**os.environ, "DATABASE_URL": url}
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=BACKEND,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, result.stderr
        engine = create_engine(url)
        tables = set(inspect(engine).get_table_names())
        engine.dispose()
    assert set(Base.metadata.tables) <= tables


def test_all_routes_use_api_prefix() -> None:
    allowed_root = {"/health", "/health/ready", "/docs", "/openapi.json", "/docs/oauth2-redirect"}
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path not in allowed_root:
            assert route.path.startswith(API_PREFIX + "/"), route.path
    assert API_PREFIX == "/api/v1"


def test_docs_hidden_unless_debug(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.config import get_settings

    monkeypatch.setenv("DEBUG", "false")
    get_settings.cache_clear()
    try:
        prod = create_app()
        assert prod.docs_url is None and prod.openapi_url is None
    finally:
        monkeypatch.undo()
        get_settings.cache_clear()


def test_login_with_seed_credentials(client: TestClient, seeded: object) -> None:
    from tests.conftest import login

    headers = login(client)
    assert headers["Authorization"].startswith("Bearer ")
