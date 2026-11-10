"""Real database: unique constraints and the savepoint paths."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import utcnow
from app.models import SyncAttempt, WellnessReading
from app.repositories.reading_repository import ReadingRepository
from app.repositories.sync_repository import SyncRepository
from tests.factories import make_connection, make_reading, make_user


def test_duplicate_key_returns_none_and_keeps_session_usable(db_session: Session) -> None:
    user = make_user(db_session)
    conn = make_connection(db_session, user)
    repo = SyncRepository(db_session)
    first = repo.start(conn.id, "k" * 16, utcnow())
    db_session.commit()
    assert first is not None
    assert repo.start(conn.id, "k" * 16, utcnow()) is None
    assert db_session.scalar(select(func.count()).select_from(SyncAttempt)) == 1
    assert repo.find(conn.id, "k" * 16) is not None


def test_duplicate_event_rejected_by_constraint(db_session: Session) -> None:
    user = make_user(db_session)
    conn = make_connection(db_session, user)
    make_reading(db_session, user, conn, source_event_id="evt-1")
    dup = WellnessReading(
        user_id=user.id,
        device_connection_id=conn.id,
        source_event_id="evt-1",
        metric_type="weight",
        value_numeric=70,
        unit="kg",
        observed_at=utcnow(),
        normalized_at=utcnow(),
    )
    assert ReadingRepository(db_session).add_unique(dup) is False
    assert db_session.scalar(select(func.count()).select_from(WellnessReading)) == 1


def test_same_event_id_allowed_on_other_connection(db_session: Session) -> None:
    user = make_user(db_session)
    a = make_connection(db_session, user, provider="wearable_platform_a")
    b = make_connection(db_session, user, provider="wearable_platform_b")
    make_reading(db_session, user, a, source_event_id="evt-1")
    make_reading(db_session, user, b, source_event_id="evt-1")
    assert ReadingRepository(db_session).existing_event_ids(uuid.uuid4(), ["evt-1"]) == set()
