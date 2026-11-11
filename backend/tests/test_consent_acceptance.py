from __future__ import annotations

from app.seed import seed_all
from tests.conftest import login

BODY = {
    "decision": "granted",
    "notice_version": "v1.0",
    "data_categories": ["weight", "steps"],
    "purpose": "wellness_support",
}


def test_requires_auth(client):
    assert client.get("/api/v1/consents/current").status_code == 401
    assert client.put("/api/v1/consents/current", json=BODY).status_code == 401


def test_get_without_record_is_null(client, seeded_accounts):
    headers = login(client, "rohan")
    response = client.get("/api/v1/consents/current", headers=headers)
    assert response.status_code == 200
    assert response.json() is None


def test_grant_stores_decision_version_timestamp(client, seeded_accounts):
    headers = login(client, "rohan")
    put = client.put("/api/v1/consents/current", json=BODY, headers=headers)
    assert put.status_code == 200
    data = put.json()
    assert data["decision"] == "granted"
    assert data["notice_version"] == "v1.0"
    assert data["collection_allowed"] is True
    assert data["data_rights_path"] is None
    assert data["recorded_at"]
    got = client.get("/api/v1/consents/current", headers=headers).json()
    assert got["id"] == data["id"]


def test_withdraw_returns_data_rights_path(client, seeded_accounts):
    headers = login(client, "rohan")
    client.put("/api/v1/consents/current", json=BODY, headers=headers)
    out = client.put(
        "/api/v1/consents/current", json={**BODY, "decision": "withdrawn"}, headers=headers
    ).json()
    assert out["collection_allowed"] is False
    assert out["data_rights_path"].startswith("/")


def test_validation(client, seeded_accounts):
    headers = login(client, "rohan")
    for bad in (
        {**BODY, "data_categories": []},
        {**BODY, "data_categories": ["blood_pressure"]},
        {**BODY, "purpose": "marketing"},
        {**BODY, "decision": "maybe"},
        {**BODY, "notice_version": ""},
        {**BODY, "notice_version": "x" * 65},
    ):
        assert client.put("/api/v1/consents/current", json=bad, headers=headers).status_code == 422


def test_seeded_consent(client, db_session, seeded_accounts):
    seed_all(db_session)
    seed_all(db_session)
    asha = client.get("/api/v1/consents/current", headers=login(client, "asha"))
    assert asha.status_code == 200
    assert asha.json()["notice_version"] == "v1.0"
    assert asha.json()["collection_allowed"] is True
    rohan = client.get("/api/v1/consents/current", headers=login(client, "rohan"))
    assert rohan.status_code == 200 and rohan.json() is None


def test_require_active_dependency_blocks_without_consent(client, seeded_accounts):
    from fastapi import Depends

    from app.deps import CurrentUser, require_active_consent
    from app.main import app

    @app.get("/_probe_consent")
    def probe(user: CurrentUser = Depends(require_active_consent)) -> dict[str, str]:
        return {"ok": "yes"}

    try:
        headers = login(client, "rohan")
        blocked = client.get("/_probe_consent", headers=headers)
        assert blocked.status_code == 403
        assert blocked.json() == {
            "detail": "Active consent is required before connecting a source"
        }
        client.put("/api/v1/consents/current", json=BODY, headers=headers)
        assert client.get("/_probe_consent", headers=headers).status_code == 200
    finally:
        app.router.routes[:] = [
            r for r in app.router.routes if getattr(r, "path", "") != "/_probe_consent"
        ]
