import uuid
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base
from app.models import ConsentRecord, User
from tests import factories as f


def test_thirteen_tables_registered() -> None:
    assert set(Base.metadata.tables) == {
        "users", "sessions", "onboarding_progress", "consent_records", "device_connections",
        "sync_attempts", "wellness_readings", "insights", "deviation_events", "alerts",
        "recommendations", "goals", "audit_logs",
    }  # fmt: skip


def test_user_id_is_integer_and_other_pks_uuid(db_session: Session) -> None:
    user = f.make_user(db_session)
    assert isinstance(user.id, int)
    conn = f.make_connection(db_session, user)
    assert isinstance(conn.id, uuid.UUID)
    assert isinstance(f.make_session(db_session, user).id, uuid.UUID)


def test_timestamps_round_trip_as_utc(db_session: Session) -> None:
    user = f.make_user(db_session)
    db_session.expire_all()
    loaded = db_session.get(User, user.id)
    assert loaded is not None and loaded.created_at.tzinfo is not None


def test_duplicate_email_rejected(db_session: Session) -> None:
    f.make_user(db_session, email="dup@example.com")
    with pytest.raises(IntegrityError):
        f.make_user(db_session, email="dup@example.com")


def test_full_graph_of_records(db_session: Session) -> None:
    user = f.make_user(db_session)
    f.make_onboarding(db_session, user)
    f.make_consent(db_session, user)
    conn = f.make_connection(db_session, user)
    f.make_sync_attempt(db_session, conn)
    reading = f.make_reading(db_session, user, conn)
    dev = f.make_deviation(db_session, user, reading)
    f.make_alert(db_session, user, dev)
    insight = f.make_insight(db_session, user)
    f.make_recommendation(db_session, user, insight)
    f.make_goal(db_session, user)
    f.make_audit(db_session, user)
    assert reading.value_numeric == Decimal("70.5000")


def test_duplicate_reading_event_rejected(db_session: Session) -> None:
    user = f.make_user(db_session)
    conn = f.make_connection(db_session, user)
    f.make_reading(db_session, user, conn, source_event_id="evt-1")
    with pytest.raises(IntegrityError):
        f.make_reading(db_session, user, conn, source_event_id="evt-1")


def test_duplicate_sync_idempotency_key_rejected(db_session: Session) -> None:
    conn = f.make_connection(db_session, f.make_user(db_session))
    f.make_sync_attempt(db_session, conn, idempotency_key="k1")
    with pytest.raises(IntegrityError):
        f.make_sync_attempt(db_session, conn, idempotency_key="k1")


@pytest.mark.parametrize(
    "maker,kwargs",
    [
        (f.make_consent, {"status": "maybe"}),
        (f.make_connection, {"status": "bogus"}),
        (f.make_insight, {"status": "draft"}),
        (f.make_goal, {"status": "archived"}),
    ],
)
def test_check_constraints_reject_bad_status(db_session: Session, maker, kwargs) -> None:  # type: ignore[no-untyped-def]
    user = f.make_user(db_session)
    with pytest.raises(IntegrityError):
        maker(db_session, user, **kwargs)


def test_alert_urgency_check(db_session: Session) -> None:
    user = f.make_user(db_session)
    reading = f.make_reading(db_session, user, f.make_connection(db_session, user))
    dev = f.make_deviation(db_session, user, reading)
    with pytest.raises(IntegrityError):
        f.make_alert(db_session, user, dev, urgency="panic")


def test_pii_tables_carry_retention_metadata() -> None:
    for name in ("users", "consent_records", "audit_logs", "wellness_readings"):
        assert Base.metadata.tables[name].info["retention_days"] > 0
    assert ConsentRecord.__table__.info["append_only"] is True  # type: ignore[attr-defined]
