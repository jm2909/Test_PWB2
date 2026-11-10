from sqlalchemy.orm import Session

from app.seeds.users import user_id
from app.services.dashboard_service import DashboardCompositionService


def test_asha_has_all_groups(seeded: Session) -> None:
    result = DashboardCompositionService(seeded).compose(user_id(seeded, "asha"))
    keys = {g.key for g in result.signal_groups}
    assert {"body_composition", "sleep", "heart_rate", "activity", "goals"} <= keys
    assert result.source_gaps == []
    assert result.display_name == "Asha"
    assert result.last_synced_at is not None
    assert result.unread_alert_count == 2
    body = next(g for g in result.signal_groups if g.key == "body_composition")
    assert body.metrics["weight_kg"] is not None and body.metrics["weight_delta_kg"] is not None
    goal = next(g for g in result.signal_groups if g.key == "goals")
    assert goal.metrics["target"] == 65.0 and goal.metrics["current"] is not None


def test_rohan_without_data_gets_gaps_not_failure(seeded: Session) -> None:
    result = DashboardCompositionService(seeded).compose(user_id(seeded, "rohan"))
    assert result.signal_groups == [] or all(g.key == "goals" for g in result.signal_groups)
    reasons = {g.key: g for g in result.source_gaps}
    assert reasons["sleep"].reason == "Your wearable has not synced sleep readings."
    assert reasons["sleep"].recovery_action == "Check wearable connection"
    assert "goals" in reasons or any(g.key == "goals" for g in result.signal_groups)


def test_missing_goal_reads_no_goal_set(seeded: Session) -> None:
    result = DashboardCompositionService(seeded).compose(user_id(seeded, "meena"))
    goal_gap = [g for g in result.source_gaps if g.key == "goals"]
    assert goal_gap and goal_gap[0].reason == "No goal set"


def test_meena_other_signals_stay_usable(seeded: Session) -> None:
    result = DashboardCompositionService(seeded).compose(user_id(seeded, "meena"))
    assert result.signal_groups or result.source_gaps
    assert len(result.signal_groups) + len(result.source_gaps) >= 5
