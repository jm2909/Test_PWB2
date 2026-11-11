from __future__ import annotations

import pytest

from app.errors import NotFoundError, PermissionDeniedError
from app.models import AuditLog, ConsentRecord
from app.schemas.consent import ConsentRequest
from app.services.consent import ConsentService


def _req(decision: str = "granted") -> ConsentRequest:
    return ConsentRequest(
        decision=decision,  # type: ignore[arg-type]
        notice_version="v1.0",
        data_categories=["weight", "steps"],
        purpose="wellness_support",
    )


def test_no_record_not_found_and_not_active(db_session, seeded_accounts):
    service = ConsentService(db_session)
    acct = seeded_accounts["rohan"].id
    with pytest.raises(NotFoundError):
        service.current(acct)
    with pytest.raises(PermissionDeniedError) as exc:
        service.require_active(acct)
    assert exc.value.detail == "Active consent is required before connecting a source"


def test_grant_then_withdraw_latest_wins(db_session, seeded_accounts):
    service = ConsentService(db_session)
    acct = seeded_accounts["rohan"].id
    granted = service.record(acct, _req("granted"))
    assert granted.collection_allowed and granted.data_rights_path is None
    service.require_active(acct)
    withdrawn = service.record(acct, _req("withdrawn"))
    assert not withdrawn.collection_allowed
    assert withdrawn.data_rights_path
    assert service.current(acct).decision == "withdrawn"
    with pytest.raises(PermissionDeniedError):
        service.require_active(acct)
    assert db_session.query(ConsentRecord).filter_by(account_id=acct).count() == 2


def test_audit_has_no_categories_or_health_values(db_session, seeded_accounts):
    service = ConsentService(db_session)
    service.record(seeded_accounts["rohan"].id, _req())
    event = db_session.query(AuditLog).filter_by(event_type="consent.recorded").one()
    assert set(event.event_metadata) == {"decision", "notice_version"}
