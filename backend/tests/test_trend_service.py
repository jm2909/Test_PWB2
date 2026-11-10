import pytest
from sqlalchemy.orm import Session

from app.seeds.users import user_id
from app.services.trend_service import TrendExplanationService, UnsupportedMetricError


def test_asha_weight_trend_available_and_chronological(seeded: Session) -> None:
    result = TrendExplanationService(seeded).trend(user_id(seeded, "asha"), "weight", 30)
    assert result.status == "available"
    times = [p.observed_at for p in result.points]
    assert times == sorted(times)
    assert result.reading_count == len(result.points) >= 25


def test_year_period_is_insufficient_for_asha(seeded: Session) -> None:
    result = TrendExplanationService(seeded).trend(user_id(seeded, "asha"), "steps", 365)
    assert result.status == "insufficient_history"
    assert "A reliable trend is not available yet." in result.explanation


def test_meena_sleep_insufficient(seeded: Session) -> None:
    result = TrendExplanationService(seeded).trend(user_id(seeded, "meena"), "sleep_duration", 30)
    assert result.status == "insufficient_history"


def test_unknown_metric_rejected(seeded: Session) -> None:
    with pytest.raises(UnsupportedMetricError):
        TrendExplanationService(seeded).trend(user_id(seeded, "asha"), "bogus", 30)
