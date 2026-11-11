from __future__ import annotations

from sqlalchemy import func, select

from app.models import Connection
from tests.conftest import login

URL = "/api/v1/connections/scale"


def _body(ident: str = "SSC-9001") -> dict[str, str]:
    return {"device_identifier": ident, "device_label": "Kitchen"}


def test_connection_scale_requires_consent(client, seeded_accounts):
    r = client.post(URL, json=_body(), headers=login(client, "rohan"))
    assert r.status_code == 403
    assert r.json() == {"detail": "Active consent is required before connecting a source"}


def test_connection_scale_requires_auth(client):
    assert client.post(URL, json=_body()).status_code == 401


def test_connection_scale_success_and_duplicate(full_seed, auth_client, db_session):
    r = auth_client.post(URL, json=_body())
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "current" and body["source"] == "scale"
    assert body["external_identifier"] == "SSC-9001" and body["recovery_action"] is None
    again = auth_client.post(URL, json=_body(), headers={"Idempotency-Key": "k1"})
    assert again.status_code == 200 and again.json()["id"] == body["id"]
    count = db_session.scalar(
        select(func.count())
        .select_from(Connection)
        .where(Connection.external_identifier == "SSC-9001")
    )
    assert count == 1


def test_connection_scale_pending(full_seed, auth_client):
    r = auth_client.post(URL, json=_body("SSC-PENDING-1"))
    assert r.status_code == 202 and r.json()["status"] == "pending"


def test_connection_scale_failure_is_safe(full_seed, auth_client):
    r = auth_client.post(URL, json=_body("SSC-FAIL-1"))
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "failed" and body["recovery_action"] == "retry_or_contact_support"
    assert body["message"] == "Connection could not be completed. Retry or contact support."
    assert "scale link failed" not in r.text
    # retry of the failed link re-attempts rather than duplicating
    retry = auth_client.post(URL, json=_body("SSC-FAIL-1"))
    assert retry.json()["id"] == body["id"]


def test_connection_scale_validation(full_seed, auth_client):
    assert (
        auth_client.post(URL, json={"device_identifier": "", "device_label": "x"}).status_code
        == 422
    )
    assert (
        auth_client.post(
            URL, json={"device_identifier": "a" * 129, "device_label": "x"}
        ).status_code
        == 422
    )


def test_connection_scale_seeded_states(db_session, full_seed):
    rows = {
        c.external_identifier: c
        for c in db_session.scalars(select(Connection).where(Connection.source == "scale"))
    }
    assert rows["SSC-0482"].status == "current" and rows["SSC-0482"].display_label == "Bathroom"
    assert rows["SSC-0517"].status == "stale" and rows["SSC-0517"].display_label == "Bedroom"
