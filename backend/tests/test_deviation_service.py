import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import DeviationEvent
from app.services.deviation_service import DeviationDetectionService
from tests.factories import make_connection, make_reading, make_user


def _load(db: Session, metric: str, unit: str, start: float, end: float, days: int = 14):
    user = make_user(db)
    conn = make_connection(db, user)
    now = datetime.now(UTC)
    readings = []
    for i in range(days + 1):
        value = start + (end - start) * i / days
        readings.append(
            make_reading(
                db,
                user,
                conn,
                metric_type=metric,
                unit=unit,
                value_numeric=Decimal(f"{value:.3f}"),
                observed_at=now - timedelta(days=days - i),
            )
        )
    return user, readings


def _codes(events: list[DeviationEvent]) -> set[str]:
    return {e.criterion_code for e in events}


def test_heart_rate_rise_and_sustained(db_session: Session) -> None:
    user, readings = _load(db_session, "resting_heart_rate", "bpm", 62, 68)
    events = DeviationDetectionService(db_session).evaluate(user.id, [r.id for r in readings])
    assert _codes(events) == {"rhr_rise_14d", "rhr_sustained_14d"}
    assert all(e.wellness_reading_id == readings[-1].id for e in events)


def test_unmet_creates_nothing(db_session: Session) -> None:
    user, readings = _load(db_session, "resting_heart_rate", "bpm", 60, 62)
    assert DeviationDetectionService(db_session).evaluate(user.id, [r.id for r in readings]) == []
    user2, r2 = _load(db_session, "weight", "kg", 70, 69.5)
    assert DeviationDetectionService(db_session).evaluate(user2.id, [r.id for r in r2]) == []


def test_sleep_decline_and_weight_change(db_session: Session) -> None:
    user, readings = _load(db_session, "sleep_hours", "h", 7.2, 6.1)
    assert _codes(DeviationDetectionService(db_session).evaluate(user.id, [r.id for r in readings])) == {
        "sleep_decline_14d"
    }
    user2, r2 = _load(db_session, "weight", "kg", 70, 67.5)
    assert _codes(DeviationDetectionService(db_session).evaluate(user2.id, [r.id for r in r2])) == {
        "weight_change_14d"
    }


def test_one_event_per_reading_criterion(db_session: Session) -> None:
    user, readings = _load(db_session, "resting_heart_rate", "bpm", 62, 68)
    svc = DeviationDetectionService(db_session)
    ids = [r.id for r in readings]
    svc.evaluate(user.id, ids)
    assert svc.evaluate(user.id, ids) == []
    count = db_session.scalar(select(func.count()).select_from(DeviationEvent))
    assert count == 2


def test_unknown_ids_ignored(db_session: Session) -> None:
    user, _ = _load(db_session, "weight", "kg", 70, 67)
    assert DeviationDetectionService(db_session).evaluate(user.id, [uuid.uuid4()]) == []
