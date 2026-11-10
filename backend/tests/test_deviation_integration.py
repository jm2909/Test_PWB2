from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import DeviationEvent, DeviceConnection
from app.seeds.users import user_id
from app.services import sync_service
from app.services.deviation_service import post_ingest_hook


def _conn(db: Session, persona: str, provider: str) -> DeviceConnection:
    conn = db.scalar(
        select(DeviceConnection).where(
            DeviceConnection.user_id == user_id(db, persona), DeviceConnection.provider == provider
        )
    )
    assert conn is not None
    return conn


def _sync(client: TestClient, headers: dict[str, str], conn: DeviceConnection, key: str) -> Any:
    return client.post(
        "/api/v1/sync",
        headers={**headers, "Idempotency-Key": key},
        json={"device_connection_id": str(conn.id)},
    )


def test_hook_registered_and_fires_on_sync(
    client: TestClient,
    seeded: Session,
    persona_headers: Callable[[str], dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert post_ingest_hook in sync_service._HOOKS
    calls: list[int] = []
    monkeypatch.setattr(sync_service, "_HOOKS", [lambda db, uid, ids: calls.append(len(ids))])
    r = _sync(
        client, persona_headers("asha"), _conn(seeded, "asha", "wearable_platform_a"), "hook-key-0123456789"
    )
    assert r.status_code == 200 and calls and calls[0] > 0


def test_failing_evaluation_is_suppressed(
    client: TestClient,
    seeded: Session,
    persona_headers: Callable[[str], dict[str, str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(self: object, *a: object, **k: object) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr("app.services.deviation_service.DeviationDetectionService.evaluate", boom)
    r = _sync(
        client, persona_headers("asha"), _conn(seeded, "asha", "wearable_platform_a"), "fail-eval-0123456789"
    )
    assert r.status_code == 200 and r.json()["status"] == "connected"


def test_sync_with_unmet_criteria_creates_nothing(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    before = seeded.scalar(select(func.count()).select_from(DeviationEvent))
    r = _sync(
        client, persona_headers("asha"), _conn(seeded, "asha", "wearable_platform_a"), "unmet-key-0123456789"
    )
    assert r.status_code == 200
    seeded.expire_all()
    # simulated adapter data does not satisfy any configured criterion over a 14-day window
    assert seeded.scalar(select(func.count()).select_from(DeviationEvent)) == before
