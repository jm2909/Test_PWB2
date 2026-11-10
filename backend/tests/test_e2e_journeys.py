"""Cross-feature acceptance journeys through the real HTTP API (FR-001..FR-024 in scope)."""

import re
import uuid
from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import API_PREFIX, app
from tests.conftest import login

NEW_EMAIL = "journey.user@example.com"
NEW_PASSWORD = "journey-pass-phrase-1"  # noqa: S105 - test credential
V = "/api/v1"


def _register_and_login(client: TestClient) -> dict[str, str]:
    created = client.post(f"{V}/accounts", json={"email": NEW_EMAIL, "password": NEW_PASSWORD})
    assert created.status_code == 201, created.text
    assert created.json()["onboarding_status"] == "not_started"
    return login(client, NEW_EMAIL, NEW_PASSWORD)


def _consent(client: TestClient, h: dict[str, str], purpose: str, status: str) -> None:
    r = client.post(f"{V}/consents", json={"purpose": purpose, "version": "1.0", "status": status}, headers=h)
    assert r.status_code in (200, 201), r.text


def _onboard(client: TestClient, h: dict[str, str]) -> None:
    r = client.put(
        f"{V}/onboarding",
        json={
            "profile": {"display_name": "Journey"},
            "goal_intent": "lose_weight",
            "device_next_step": "scale",
        },
        headers=h,
    )
    assert r.status_code == 200, r.text
    assert r.json()["remaining_steps"] == ["consent"]


def _pair_scale(client: TestClient, h: dict[str, str]) -> dict[str, object]:
    r = client.post(
        f"{V}/device-connections",
        json={"provider": "sapphire_scale", "connection_mode": "pair"},
        headers=h,
    )
    assert r.status_code in (200, 201), r.text
    body: dict[str, object] = r.json()
    assert body["status"] == "connected"
    return body


def _sync(
    client: TestClient, h: dict[str, str], conn_id: object, key: str | None = None
) -> dict[str, object]:
    r = client.post(
        f"{V}/sync",
        json={"device_connection_id": conn_id},
        headers={**h, "Idempotency-Key": key or uuid.uuid4().hex},
    )
    assert r.status_code == 200, r.text
    body: dict[str, object] = r.json()
    return body


def test_full_journey_register_to_recommendation(client: TestClient, seeded: Session) -> None:
    h = _register_and_login(client)
    assert client.get(f"{V}/onboarding", headers=h).json()["status"] == "not_started"
    _onboard(client, h)
    _consent(client, h, "device_processing", "accepted")
    _consent(client, h, "personalized_insights", "accepted")
    done = client.get(f"{V}/onboarding", headers=h).json()
    assert done["remaining_steps"] == []
    assert len(client.get(f"{V}/consents", headers=h).json()["latest"]) == 2

    conn = _pair_scale(client, h)
    summary = _sync(client, h, conn["id"])
    assert summary["status"] == "connected"
    assert summary["last_sync_summary"]["new_readings"] > 0  # type: ignore[index]

    dash = client.get(f"{V}/dashboard", headers=h).json()
    groups = {g["group"] for g in dash["signal_groups"]}
    assert "body_composition" in groups
    assert {g["group"] for g in dash["source_gaps"]}  # other sources missing -> explained gaps
    assert all(g["reason"] for g in dash["source_gaps"])

    trend = client.get(f"{V}/trends", params={"metric_type": "weight", "period_days": 30}, headers=h).json()
    assert trend["status"] in ("available", "insufficient_history")
    assert trend["explanation"]
    expl = client.post(
        f"{V}/metric-explanations", json={"metric_type": "weight", "period_days": 30}, headers=h
    )
    assert expl.status_code == 200 and expl.json()["explanation"]

    ins = client.post(f"{V}/insights", headers=h)
    assert ins.status_code in (200, 201), ins.text
    assert ins.json()["status"] in ("published", "suppressed")
    if ins.json()["status"] == "suppressed":
        assert ins.json()["observed_trend"] is None  # no unsupported conclusion
    rec = client.get(f"{V}/recommendations", headers=h).json()
    assert rec["status"] in ("available", "none")
    if rec["status"] == "none":
        assert rec["action_text"] is None


def test_registration_rejections(client: TestClient, seeded: Session) -> None:
    assert (
        client.post(
            f"{V}/accounts", json={"email": "asha.menon@example.com", "password": NEW_PASSWORD}
        ).status_code
        == 409
    )
    assert (
        client.post(f"{V}/accounts", json={"email": "not-an-email", "password": NEW_PASSWORD}).status_code
        == 422
    )
    assert (
        client.post(f"{V}/accounts", json={"email": "x@example.com", "password": "short"}).status_code == 422
    )
    bad = client.post(
        f"{V}/auth/sessions", json={"email": "asha.menon@example.com", "password": "wrong-password-1"}
    )
    assert bad.status_code == 401


def test_consent_decline_blocks_processing(client: TestClient, seeded: Session) -> None:
    h = _register_and_login(client)
    _consent(client, h, "device_processing", "declined")
    _consent(client, h, "personalized_insights", "declined")
    blocked = client.post(
        f"{V}/device-connections", json={"provider": "sapphire_scale", "connection_mode": "pair"}, headers=h
    )
    assert blocked.status_code == 403 and blocked.json()["detail"]
    insight = client.post(f"{V}/insights", headers=h)
    assert insight.status_code == 403 and insight.json()["detail"]
    assert client.get(f"{V}/insights", headers=h).json()["total"] == 0


def test_duplicate_sync_is_idempotent(client: TestClient, seeded: Session) -> None:
    h = _register_and_login(client)
    _consent(client, h, "device_processing", "accepted")
    conn = _pair_scale(client, h)
    key = "idem-key-0123456789"
    first = _sync(client, h, conn["id"], key)
    n = first["last_sync_summary"]["new_readings"]  # type: ignore[index]
    assert n > 0
    again = _sync(client, h, conn["id"], key)
    assert again["last_sync_summary"]["new_readings"] == n  # type: ignore[index]
    redelivery = _sync(client, h, conn["id"], "different-key-0123456789")
    assert redelivery["last_sync_summary"]["new_readings"] == 0  # type: ignore[index]
    assert redelivery["last_sync_summary"]["duplicates"] > 0  # type: ignore[index]
    trend = client.get(f"{V}/trends", params={"metric_type": "weight", "period_days": 30}, headers=h).json()
    assert trend["reading_count"] == len(trend["points"])
    assert trend["reading_count"] == n or trend["reading_count"] <= n


def test_failed_sync_then_retry(client: TestClient, persona_headers: Callable[[str], dict[str, str]]) -> None:
    h = persona_headers("asha")
    conns = client.get(f"{V}/device-connections", headers=h).json()["items"]
    b = next(c for c in conns if c["provider"] == "wearable_platform_b")
    assert b["status"] == "failed" and b["failure_reason"] and b["recovery_action"]
    failed = _sync(client, h, b["id"], "sim-fail-0123456789ab")
    assert failed["status"] == "failed" and failed["recovery_action"]
    ok = _sync(client, h, b["id"])
    assert ok["status"] == "connected" and ok["last_successful_sync_at"]
    c = next(c for c in conns if c["provider"] == "wearable_platform_c")
    assert c["status"] == "revoked" and c["recovery_action"]
    assert _sync(client, h, c["id"])["status"] == "revoked"  # never silently current


def test_deviation_to_alert_chain(
    client: TestClient, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    asha = persona_headers("asha")
    events = client.get(f"{V}/deviation-events", headers=asha).json()
    assert events["total"] >= 1
    alerts = client.get(f"{V}/alerts", headers=asha).json()
    assert alerts["total"] >= 1
    for a in alerts["items"]:
        assert a["trend_name"] and a["recommended_next_action"] and a["urgency"]
        assert "diagnos" not in (a["what_we_saw"] + a["recommended_next_action"]).lower().replace(
            "not diagnos", ""
        )
    urgent = [a for a in alerts["items"] if a["urgency"] != "routine"]
    for a in urgent:
        assert a["care_direction"] and "professional" in a["care_direction"].lower()
    # no deviation -> no alerts for a user without events
    meena = persona_headers("meena")
    assert client.get(f"{V}/deviation-events", headers=meena).json()["total"] == 0
    assert client.get(f"{V}/alerts", headers=meena).json()["total"] == 0


def test_goal_and_insight_recommendation(
    client: TestClient, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    h = persona_headers("asha")
    ok = client.post(
        f"{V}/goals",
        json={"goal_type": "sleep_improvement", "target_value": 8, "target_unit": "h"},
        headers=h,
    )
    assert ok.status_code == 201
    bad = client.post(
        f"{V}/goals", json={"goal_type": "weight_loss", "target_value": -5, "target_unit": "kg"}, headers=h
    )
    assert bad.status_code == 422 and bad.json()["detail"]
    types = {g["goal_type"] for g in client.get(f"{V}/goals", headers=h).json()["items"]}
    assert "sleep_improvement" in types
    rec = client.get(f"{V}/recommendations", headers=h).json()
    assert rec["status"] == "available" and rec["action_text"] and rec["reason_text"]
    mh = persona_headers("meena")
    assert client.get(f"{V}/recommendations", headers=mh).json()["status"] == "none"
    insights = client.get(f"{V}/insights", headers=mh).json()["items"]
    assert all(i["status"] == "suppressed" for i in insights)


def _operations() -> list[tuple[str, str]]:
    """(METHOD, path) for every operation the app exposes, from its OpenAPI schema."""
    paths = app.openapi()["paths"]
    return [
        (m.upper(), p)
        for p, ops in paths.items()
        for m in ops
        if m in ("get", "post", "put", "patch", "delete")
    ]


def test_all_routes_prefixed_and_no_deferred() -> None:
    assert API_PREFIX == V
    ops = _operations()
    assert len(ops) >= 15
    for _, path in ops:
        assert path.startswith(V) or path in ("/health", "/health/ready"), path
    deferred = ("marketplace", "partner", "subscription", "support", "admin", "coach", "community")
    for _, path in ops:
        assert not any(d in path for d in deferred), path


def test_every_protected_route_requires_auth(client: TestClient) -> None:
    public = {(f"{V}/accounts", "POST"), (f"{V}/auth/sessions", "POST")}
    checked = 0
    for method, path in _operations():
        if not path.startswith(V) or (path, method) in public:
            continue
        resp = client.request(method, re.sub(r"\{[^}]+\}", str(uuid.uuid4()), path), json={})
        assert resp.status_code == 401, (method, path, resp.status_code)
        checked += 1
    assert checked >= 15
    assert client.get(f"{V}/dashboard", headers={"Authorization": "Bearer bogus"}).status_code == 401


def test_logout_revokes_and_hides_data(client: TestClient, seeded: Session) -> None:
    h = login(client)
    assert client.get(f"{V}/dashboard", headers=h).status_code == 200
    assert client.delete(f"{V}/auth/sessions/current", headers=h).status_code == 204
    assert client.get(f"{V}/dashboard", headers=h).status_code == 401


def test_owner_isolation(client: TestClient, persona_headers: Callable[[str], dict[str, str]]) -> None:
    asha = persona_headers("asha")
    rohan = persona_headers("rohan")
    asha_conn = client.get(f"{V}/device-connections", headers=asha).json()["items"][0]
    rohan_ids = {c["id"] for c in client.get(f"{V}/device-connections", headers=rohan).json()["items"]}
    assert asha_conn["id"] not in rohan_ids
    cross = client.post(
        f"{V}/sync",
        json={"device_connection_id": asha_conn["id"]},
        headers={**rohan, "Idempotency-Key": uuid.uuid4().hex},
    )
    assert cross.status_code in (403, 404)
    rohan_goals = client.get(f"{V}/goals", headers=rohan).json()["items"]
    assert all(g["goal_type"] != "weight_loss" for g in rohan_goals)
    assert client.get(f"{V}/alerts", headers=rohan).json()["total"] == 0


@pytest.mark.parametrize("path", ["/health", "/health/ready"])
def test_health_is_public(client: TestClient, path: str) -> None:
    assert client.get(path).status_code == 200
