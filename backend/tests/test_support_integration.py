from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models import Connection, SupportRequest, WellnessAlert
from tests.conftest import login

URL = "/api/v1/support-requests"


def _body(**kw):
    data = {"category": "connection", "description": "Help please", "context_type": "account"}
    return {**data, **kw}


def test_support_integration_requires_auth(client):
    assert client.post(URL, json=_body()).status_code == 401


def test_support_integration_account_context(auth_client, db_session):
    r = auth_client.post(URL, json=_body())
    assert r.status_code == 201, r.text
    body = r.json()
    assert set(body) == {"id", "reference", "status", "submitted_at"}
    assert body["status"] == "submitted"
    assert db_session.scalar(
        select(SupportRequest).where(SupportRequest.reference == body["reference"])
    )


def test_support_integration_device_and_alert_ownership(client, full_seed, db_session):
    asha = login(client, "asha")
    rohan = login(client, "rohan")
    conn = db_session.scalars(select(Connection)).first()
    alert = db_session.scalars(select(WellnessAlert)).first()
    assert conn is not None and alert is not None
    ok = client.post(URL, json=_body(context_type="device", context_id=str(conn.id)), headers=asha)
    assert ok.status_code == 201
    ok = client.post(
        URL,
        json=_body(category="alert", context_type="alert", context_id=str(alert.id)),
        headers=asha,
    )
    assert ok.status_code == 201
    for ctx, cid in (("device", conn.id), ("alert", alert.id), ("device", uuid.uuid4())):
        r = client.post(URL, json=_body(context_type=ctx, context_id=str(cid)), headers=rohan)
        assert r.status_code == 404


def test_support_integration_invalid_bodies(auth_client):
    assert auth_client.post(URL, json=_body(category="x")).status_code == 422
    assert auth_client.post(URL, json=_body(description="")).status_code == 422
    assert auth_client.post(URL, json=_body(context_type="other")).status_code == 422
    assert auth_client.post(URL, json=_body(context_id="nope")).status_code == 422
