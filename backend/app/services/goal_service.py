"""Goals: validate the target per type, then save. An invalid target never creates a row."""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Goal
from app.repositories.goal_repository import GoalRepository
from app.schemas.goal_schemas import GoalCreate
from app.services.audit_service import AuditService


class InvalidGoalError(Exception):
    def __init__(self, guidance: str) -> None:
        super().__init__(guidance)
        self.guidance = guidance


@dataclass(frozen=True)
class _Rule:
    unit: str
    low: Decimal
    high: Decimal
    example: str


RULES: dict[str, _Rule] = {
    "weight_loss": _Rule("kg", Decimal(30), Decimal(250), "65"),
    "muscle_gain": _Rule("kg", Decimal(30), Decimal(250), "72"),
    "sleep_improvement": _Rule("h", Decimal(4), Decimal(12), "7.5"),
    "blood_pressure_control": _Rule("mmHg", Decimal(70), Decimal(200), "120"),
}


class GoalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = GoalRepository(db)
        self.audit = AuditService(db)

    @staticmethod
    def validate(payload: GoalCreate) -> None:
        value = payload.target_value
        unit = payload.target_unit.strip()
        rule = RULES.get(payload.goal_type)
        if rule is None:  # other_supported: any positive target with a unit
            if not value.is_finite() or value <= 0 or not unit:
                raise InvalidGoalError("Enter a target above 0 with a unit, for example 10 sessions.")
            return
        guidance = (
            f"Enter a target above 0 {rule.unit} that is realistic for you, for example {rule.example}."
        )
        if not value.is_finite() or value <= 0:
            raise InvalidGoalError(guidance)
        if unit != rule.unit:
            raise InvalidGoalError(f"Use {rule.unit} as the unit for this goal. {guidance}")
        if not (rule.low <= value <= rule.high):
            raise InvalidGoalError(
                f"Enter a target between {rule.low} and {rule.high} {rule.unit}, for example {rule.example}."
            )

    def create(self, user_id: int, payload: GoalCreate, correlation_id: str) -> Goal:
        try:
            self.validate(payload)
        except InvalidGoalError:
            self.audit.record(
                action="goal.set",
                outcome="rejected_invalid_target",
                correlation_id=correlation_id,
                user_id=user_id,
                severity="warning",
                entity_type="goal",
            )
            self.db.commit()
            raise
        row = self.repo.save_active(
            user_id, payload.goal_type, payload.target_value, payload.target_unit.strip()
        )
        self.audit.record(
            action="goal.set",
            outcome="saved",
            correlation_id=correlation_id,
            user_id=user_id,
            entity_type="goal",
            entity_id=str(row.id),
        )
        self.db.commit()
        self.db.refresh(row)
        return row

    def list_active(self, user_id: int) -> list[Goal]:
        return self.repo.list_active(user_id)
