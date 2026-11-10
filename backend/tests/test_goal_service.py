from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AuditLog, Goal
from app.schemas.goal_schemas import GoalCreate
from app.seeds.users import user_id
from app.services.goal_service import GoalService, InvalidGoalError


def goal(goal_type: str, value: str, unit: str) -> GoalCreate:
    return GoalCreate.model_validate({"goal_type": goal_type, "target_value": value, "target_unit": unit})


@pytest.mark.parametrize(
    ("gt", "value", "unit"),
    [
        ("weight_loss", "0", "kg"),
        ("weight_loss", "-5", "kg"),
        ("weight_loss", "5", "kg"),
        ("weight_loss", "65", "lb"),
        ("sleep_improvement", "20", "h"),
        ("blood_pressure_control", "120", "kg"),
        ("other_supported", "0", "sessions"),
        ("other_supported", "3", " "),
    ],
)
def test_invalid_never_creates_row(seeded: Session, gt: str, value: str, unit: str) -> None:
    uid = user_id(seeded, "rohan")
    with pytest.raises(InvalidGoalError):
        GoalService(seeded).create(uid, goal(gt, value, unit), "c")
    assert seeded.scalar(select(func.count()).select_from(Goal).where(Goal.user_id == uid)) == 0
    assert (
        seeded.scalar(select(AuditLog.outcome).where(AuditLog.action == "goal.set"))
        == "rejected_invalid_target"
    )


def test_guidance_text(seeded: Session) -> None:
    with pytest.raises(InvalidGoalError) as e:
        GoalService(seeded).create(user_id(seeded, "rohan"), goal("weight_loss", "0", "kg"), "c")
    assert e.value.guidance == "Enter a target above 0 kg that is realistic for you, for example 65."


def test_newest_replaces_same_type(seeded: Session) -> None:
    svc = GoalService(seeded)
    uid = user_id(seeded, "asha")
    svc.create(uid, goal("weight_loss", "62", "kg"), "c")
    active = [g for g in svc.list_active(uid) if g.goal_type == "weight_loss"]
    assert len(active) == 1 and active[0].target_value == Decimal(62)


def test_each_type_saved(seeded: Session) -> None:
    svc = GoalService(seeded)
    uid = user_id(seeded, "rohan")
    for gt, v, u in [
        ("muscle_gain", "75", "kg"),
        ("sleep_improvement", "7.5", "h"),
        ("blood_pressure_control", "120", "mmHg"),
        ("other_supported", "10", "sessions"),
    ]:
        svc.create(uid, goal(gt, v, u), "c")
    assert len(svc.list_active(uid)) == 4
