from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError
from sqlalchemy import select

from app.errors import NotFoundError
from app.models import AuditLog, SupportRequest
from app.schemas.support import SupportRequestCreate
from app.services.support import SupportService


def _cmd(**kw):
    data = {
        "category": "connection",
        "description": "Scale will not sync",
        "context_type": "account",
    }
    return SupportRequestCreate(**{**data, **kw})


def test_support_service_creates_reference_and_audit(db_session, factories):
    account = factories.account()
    result = SupportService(db_session).submit(account.id, _cmd())
    assert result.reference.startswith("SUP-")
    assert result.status == "submitted"
    row = db_session.scalar(select(SupportRequest))
    assert row is not None and row.account_id == account.id
    audit = db_session.scalars(
        select(AuditLog).where(AuditLog.event_type == "support.submitted")
    ).all()
    assert len(audit) == 1
    assert "Scale will not sync" not in str(audit[0].event_metadata)


def test_support_service_validation():
    with pytest.raises(ValidationError):
        _cmd(category="other")
    with pytest.raises(ValidationError):
        _cmd(description="")
    with pytest.raises(ValidationError):
        _cmd(description="x" * 2001)
    with pytest.raises(ValidationError):
        _cmd(context_type="account", context_id=uuid.uuid4())


def test_support_service_device_context_ownership(db_session, factories):
    mine = factories.account()
    other = factories.account()
    theirs = factories.connection(other)
    own = factories.connection(mine)
    service = SupportService(db_session)
    assert service.submit(mine.id, _cmd(context_type="device", context_id=own.id)).id
    with pytest.raises(NotFoundError):
        service.submit(mine.id, _cmd(context_type="device", context_id=theirs.id))
    with pytest.raises(NotFoundError):
        service.submit(mine.id, _cmd(context_type="device", context_id=uuid.uuid4()))
