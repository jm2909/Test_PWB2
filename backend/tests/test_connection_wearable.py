from sqlalchemy import select

from app.models import Connection

PUT = {
    "decision": "granted",
    "notice_version": "v1.0",
    "data_categories": ["steps"],
    "purpose": "wellness_support",
}


def _auth(client, provider="fitband"):
    return client.post(f"/api/v1/connections/wearables/{provider}/authorizations")


def test_connection_wearable_providers_listed(client, auth_headers):
    r = client.get("/api/v1/connections/providers", headers=auth_headers("asha"))
    assert r.status_code == 200
    names = {p["provider"] for p in r.json()}
    assert names == {"fitband", "pulsewear"}
    assert set(r.json()[0]) == {"provider", "display_name", "authorization_mode"}
    assert client.get("/api/v1/connections/providers").status_code == 401


def test_connection_wearable_unknown_provider_404(client, auth_headers):
    r = client.post(
        "/api/v1/connections/wearables/nope/authorizations", headers=auth_headers("asha")
    )
    assert r.status_code == 404
    assert r.json() == {"detail": "Wearable provider is not supported"}


def test_connection_wearable_requires_consent(client, auth_headers):
    r = client.post(
        "/api/v1/connections/wearables/fitband/authorizations", headers=auth_headers("rohan")
    )
    assert r.status_code == 403


def _begin(client, headers, provider="fitband"):
    r = client.post(f"/api/v1/connections/wearables/{provider}/authorizations", headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def test_connection_wearable_authorize_and_callback(client, db_session, auth_headers):
    h = auth_headers("rohan")
    assert client.put("/api/v1/consents/current", headers=h, json=PUT).status_code in (200, 201)
    start = _begin(client, h)
    assert start["authorization_url"] and start["expires_at"]
    state = start["authorization_url"].split("state=")[1]
    cb = client.post(
        "/api/v1/connections/wearables/fitband/callbacks",
        headers=h,
        json={"connection_id": start["connection_id"], "state": state, "code": "ok"},
    )
    assert cb.status_code == 200, cb.text
    body = cb.json()
    assert body["source"] == "wearable" and body["authorization_state"] == "authorized"
    assert body["recovery_action"] is None
    # re-authorizing reuses the single association
    start2 = _begin(client, h)
    assert len(db_session.scalars(select(Connection)).all()) == 1
    assert start2["connection_id"] == start["connection_id"]


def test_connection_wearable_bad_state_leaves_retry(client, db_session, auth_headers):
    h = auth_headers("rohan")
    client.put("/api/v1/consents/current", headers=h, json=PUT)
    start = _begin(client, h)
    cb = client.post(
        "/api/v1/connections/wearables/fitband/callbacks",
        headers=h,
        json={"connection_id": start["connection_id"], "state": "forged"},
    )
    assert cb.status_code == 200
    assert cb.json()["status"] == "failed"
    assert cb.json()["recovery_action"] == "retry_or_disconnect"
    assert client.get("/api/v1/dashboard", headers=h).status_code == 200  # account usable
    retry = _begin(client, h)
    assert retry["connection_id"] == start["connection_id"]


def test_connection_wearable_denied_callback_and_isolation(client, auth_headers):
    asha, rohan = auth_headers("asha"), auth_headers("rohan")
    client.put("/api/v1/consents/current", headers=asha, json=PUT)
    start = _begin(client, asha)
    denied = client.post(
        "/api/v1/connections/wearables/fitband/callbacks",
        headers=asha,
        json={"connection_id": start["connection_id"], "state": "x", "error": "access_denied"},
    )
    assert denied.json()["status"] == "failed"
    stolen = client.post(
        "/api/v1/connections/wearables/fitband/callbacks",
        headers=rohan,
        json={"connection_id": start["connection_id"], "state": "x"},
    )
    assert stolen.status_code == 404
