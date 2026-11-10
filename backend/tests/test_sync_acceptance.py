from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import DeviceConnection, WellnessReading
from app.seeds.users import user_id

URL = "/api/v1/sync"
KEY = "accept-key-0123456789"


def _conn(db: Session, persona: str, provider: str) -> DeviceConnection:
    conn = db.scalar(
        select(DeviceConnection).where(
            DeviceConnection.user_id == user_id(db, persona), DeviceConnection.provider == provider
        )
    )
    assert conn is not None
    return conn


def _post(client: TestClient, headers: dict[str, str], conn: DeviceConnection, key: str | None) -> Any:
    h = dict(headers)
    if key:
        h["Idempotency-Key"] = key
    return client.post(URL, headers=h, json={"device_connection_id": str(conn.id)})


def test_requires_auth_and_header(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    conn = _conn(seeded, "asha", "wearable_platform_a")
    assert _post(client, {}, conn, KEY).status_code == 401
    headers = persona_headers("asha")
    assert _post(client, headers, conn, None).status_code == 422
    assert _post(client, headers, conn, "short").status_code == 422
    assert client.post(URL, headers={**headers, "Idempotency-Key": KEY}, json={}).status_code == 422


def test_success_then_duplicate_delivery(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    headers = persona_headers("asha")
    conn = _conn(seeded, "asha", "wearable_platform_a")
    r = _post(client, headers, conn, KEY)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "connected" and body["last_successful_sync_at"]
    assert body["last_sync_summary"]["new_readings"] > 0
    count = seeded.scalar(select(func.count()).select_from(WellnessReading))
    again = _post(client, headers, conn, KEY).json()
    assert again["last_sync_summary"]["new_readings"] == body["last_sync_summary"]["new_readings"]
    redelivered = _post(client, headers, conn, "another-key-0123456789").json()["last_sync_summary"]
    assert redelivered["new_readings"] == 0 and redelivered["duplicates"] > 0
    seeded.expire_all()
    assert seeded.scalar(select(func.count()).select_from(WellnessReading)) == count


def test_failure_then_retry_success(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    headers = persona_headers("asha")
    conn = _conn(seeded, "asha", "wearable_platform_b")
    assert conn.status == "failed"
    r = _post(client, headers, conn, "sim-fail-0123456789abc")
    assert r.status_code == 200
    assert r.json()["status"] == "failed" and r.json()["recovery_action"] == "Retry"
    assert r.json()["failure_reason"]
    ok = _post(client, headers, conn, "retry-key-0123456789").json()
    assert ok["status"] == "connected" and ok["failure_reason"] is None and ok["recovery_action"] is None
    assert ok["last_successful_sync_at"] and ok["last_sync_summary"]["new_readings"] > 0


def test_revoked_stays_actionable(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    headers = persona_headers("asha")
    conn = _conn(seeded, "asha", "wearable_platform_c")
    body = _post(client, headers, conn, KEY).json()
    assert body["status"] == "revoked" and body["recovery_action"] == "Reconnect"
    assert body["last_sync_summary"]["new_readings"] == 0


def test_permission_issue_is_action_required(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    headers = persona_headers("asha")
    conn = _conn(seeded, "asha", "wearable_platform_a")
    body = _post(client, headers, conn, "sim-permission-0123456789").json()
    assert body["status"] == "action_required" and body["recovery_action"] == "Review permissions"


def test_consent_declined_is_403(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    headers = persona_headers("meena")  # no accepted device-processing consent
    conn = _conn(seeded, "meena", "wearable_platform_a")
    r = _post(client, headers, conn, KEY)
    assert r.status_code == 403
    assert (
        seeded.scalar(
            select(func.count())
            .select_from(WellnessReading)
            .where(WellnessReading.device_connection_id == conn.id)
        )
        == 0
    )


def test_not_owner_is_404(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    conn = _conn(seeded, "asha", "wearable_platform_a")
    assert _post(client, persona_headers("rohan"), conn, KEY).status_code == 404
