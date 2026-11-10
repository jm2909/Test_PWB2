from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.models import WellnessReading
from app.services.explanation_service import UNAVAILABLE_TEXT, TrendExplanationService
from app.services.trend_service import UnsupportedMetricError
from tests.factories import make_connection, make_reading, make_user


def _series(db: Session, metric: str, unit: str, start: float, end: float, days: int = 30) -> int:
    user = make_user(db)
    conn = make_connection(db, user)
    now = datetime.now(UTC)
    for i in range(days + 1):
        value = start + (end - start) * i / days
        make_reading(
            db,
            user,
            conn,
            metric_type=metric,
            unit=unit,
            value_numeric=Decimal(f"{value:.3f}"),
            observed_at=now - timedelta(days=days - i),
        )
    return user.id


def test_weight_down_explained_non_diagnostically(db_session: Session) -> None:
    uid = _series(db_session, "weight", "kg", 70.1, 68.4, days=29)
    result = TrendExplanationService(db_session).explain(uid, "weight", 30)
    assert result.status == "available" and result.direction == "down"
    assert "1.7 kg" in result.explanation and "Day-to-day changes are normal" in result.explanation
    assert result.reading_count == 30


def test_up_and_steady(db_session: Session) -> None:
    up = _series(db_session, "resting_heart_rate", "bpm", 60, 68)
    assert TrendExplanationService(db_session).explain(up, "resting_heart_rate", 30).direction == "up"
    flat = _series(db_session, "steps", "steps", 8000, 8010)
    assert TrendExplanationService(db_session).explain(flat, "steps", 30).direction == "steady"


def test_body_fat_unavailable(db_session: Session) -> None:
    uid = _series(db_session, "body_fat", "%", 24, 23)
    result = TrendExplanationService(db_session).explain(uid, "body_fat", 30)
    assert result.status == "unavailable" and result.direction is None
    assert result.explanation == UNAVAILABLE_TEXT


def test_insufficient_history_and_unknown_metric(db_session: Session) -> None:
    user = make_user(db_session)
    assert TrendExplanationService(db_session).explain(user.id, "weight", 30).status == "insufficient_history"
    with pytest.raises(UnsupportedMetricError):
        TrendExplanationService(db_session).explain(user.id, "mood", 30)


def test_readings_are_not_mutated(db_session: Session) -> None:
    uid = _series(db_session, "weight", "kg", 70, 69)
    TrendExplanationService(db_session).explain(uid, "weight", 30)
    assert db_session.query(WellnessReading).filter_by(user_id=uid).count() == 31
