from __future__ import annotations

from sqlalchemy import select

from app.models import AuditLog, SupportRequest

URL = "/api/v1/support-requests"


def test_support_acceptance_contexts_available(auth_client):
    for ctx in ("device", "account", "alert"):
        r = auth_client.post(
            URL, json={"category": "account", "description": "question", "context_type": ctx}
        )
        assert r.status_code == 201, r.text


def test_support_acceptance_no_health_values_required_and_reference_returned(auth_client):
    r = auth_client.post(
        URL,
        json={
            "category": "data_quality",
            "description": "Numbers look off",
            "context_type": "account",
        },
    )
    assert r.status_code == 201
    assert r.json()["reference"]


def test_support_acceptance_references_unique(auth_client):
    refs = {
        auth_client.post(
            URL, json={"category": "alert", "description": "hi", "context_type": "account"}
        ).json()["reference"]
        for _ in range(3)
    }
    assert len(refs) == 3


def test_support_acceptance_no_internal_details_exposed(auth_client, db_session):
    r = auth_client.post(
        URL,
        json={"category": "connection", "description": "secret-note", "context_type": "account"},
    )
    text = r.text.lower()
    for word in ("secret-note", "password", "token", "adapter", "traceback", "log"):
        assert word not in text
    row = db_session.scalar(select(SupportRequest))
    assert row is not None
    audit = db_session.scalars(
        select(AuditLog).where(AuditLog.event_type == "support.submitted")
    ).all()
    assert audit and all("secret-note" not in str(a.event_metadata) for a in audit)


def test_support_acceptance_seed_has_asha_request(full_seed, db_session):
    rows = db_session.scalars(select(SupportRequest)).all()
    assert len(rows) == 1 and rows[0].status == "submitted"
