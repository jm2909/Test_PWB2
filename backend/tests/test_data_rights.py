from __future__ import annotations

from sqlalchemy import select

from app.models import AuditLog, DataRightsRequest
from app.schemas.data_rights import DataRightsRequestCreate
from app.services.data_rights import DataRightsService
from tests.conftest import login


def test_data_rights_service_sets_reference_and_deadline(db_session, factories):
    account = factories.account()
    result = DataRightsService(db_session).submit(
        account.id, DataRightsRequestCreate(request_type="export")
    )
    assert result.reference.startswith("DR-")
    assert result.status == "submitted"
    assert (result.fulfillment_due_at - result.requested_at).days == 30


def test_data_rights_post_records_request_and_audit_without_health_values(
    full_seed, auth_client, db_session
):
    r = auth_client.post(
        "/api/v1/data-rights-requests",
        json={"request_type": "deletion", "description": "please delete my account"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["request_type"] == "deletion" and body["status"] == "submitted"
    row = db_session.scalar(
        select(DataRightsRequest).where(DataRightsRequest.reference == body["reference"])
    )
    assert row is not None
    audit = db_session.scalars(
        select(AuditLog).where(AuditLog.event_type == "data_rights.requested")
    ).all()
    assert len(audit) == 1
    assert "delete my account" not in str(audit[0].event_metadata)


def test_data_rights_validation(auth_client):
    assert (
        auth_client.post("/api/v1/data-rights-requests", json={"request_type": "other"}).status_code
        == 422
    )
    assert (
        auth_client.post(
            "/api/v1/data-rights-requests",
            json={"request_type": "export", "description": "x" * 1001},
        ).status_code
        == 422
    )
    assert (
        auth_client.post(
            "/api/v1/data-rights-requests",
            json={"request_type": "export", "description": "my weight is 82 kg"},
        ).status_code
        == 422
    )


def test_data_rights_requires_auth(client):
    assert client.get("/api/v1/data-rights-requests").status_code == 401
    assert (
        client.post("/api/v1/data-rights-requests", json={"request_type": "export"}).status_code
        == 401
    )


def test_data_rights_list_is_owner_only_and_paginated(client, full_seed):
    headers = login(client, "asha")
    page = client.get("/api/v1/data-rights-requests?limit=1", headers=headers).json()
    assert page["total"] == 2 and len(page["items"]) == 1 and page["limit"] == 1
    other = client.get("/api/v1/data-rights-requests", headers=login(client, "rohan")).json()
    assert other == {"items": [], "limit": 25, "offset": 0, "total": 0}
