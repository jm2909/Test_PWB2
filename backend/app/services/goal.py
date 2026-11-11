"""GoalService: wellness goals with progress from readings or an explicit data gap (FR-017)."""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session as DbSession

from app.clock import Clock, SystemClock, ensure_utc
from app.errors import ConflictError, DomainError, NotFoundError
from app.models import WellnessGoal
from app.repositories.goal import GoalRepository
from app.repositories.reading import ReadingRepository
from app.schemas.common import Page
from app.schemas.goal import GoalCreateRequest, GoalResponse
from app.services.audit import AuditService
from app.services.reading import METRICS

CATEGORY_METRICS: dict[str, tuple[str, ...]] = {
    "weight_management": ("weight", "body_fat_percentage"),
    "fitness": ("steps", "active_minutes", "resting_heart_rate"),
    "sleep_improvement": ("sleep_duration",),
    "general_wellness": tuple(METRICS),
}
TRANSITIONS: dict[str, set[str]] = {
    "active": {"paused", "closed"},
    "paused": {"active", "closed"},
    "closed": set(),
}


class GoalValidationError(DomainError):
    status_code = 422
    default_detail = "Goal is not valid"


class GoalService:
    def __init__(self, db: DbSession, clock: Clock | None = None) -> None:
        self.db = db
        self.clock = clock or SystemClock()
        self.repo = GoalRepository(db)
        self.readings = ReadingRepository(db)
        self.audit = AuditService(db, self.clock)

    def _progress(self, goal: WellnessGoal) -> GoalResponse:
        latest = self.readings.latest_for_metric(goal.account_id, goal.metric_type)
        current: Decimal | None = None
        if latest is not None and ensure_utc(latest.captured_at) >= ensure_utc(goal.created_at):
            current = Decimal(latest.value)
        return GoalResponse(
            id=goal.id,
            state=goal.state,
            category=goal.category,
            metric_type=goal.metric_type,
            target_value=goal.target_value,
            target_unit=goal.target_unit,
            target_date=goal.target_date,
            progress_status="available" if current is not None else "data_gap",
            current_value=current,
        )

    def _today(self) -> date:
        return self.clock.utc_now().date()

    def create(self, account_id: uuid.UUID, body: GoalCreateRequest) -> GoalResponse:
        if body.metric_type not in CATEGORY_METRICS[body.category]:
            raise GoalValidationError("Metric is not supported for this goal category")
        if body.target_unit != METRICS[body.metric_type][0]:
            raise GoalValidationError("Target unit does not match the metric")
        if body.target_date <= self._today():
            raise GoalValidationError("Target date must be in the future")
        now = self.clock.utc_now()
        goal = self.repo.add(
            WellnessGoal(
                account_id=account_id,
                category=body.category,
                metric_type=body.metric_type,
                target_value=body.target_value,
                target_unit=body.target_unit,
                target_date=body.target_date,
                state="active",
                created_at=now,
                updated_at=now,
            )
        )
        self.audit.record(
            "goal.created",
            entity_type="goal",
            account_id=account_id,
            entity_id=goal.id,
            metadata={"category": goal.category, "metric_type": goal.metric_type},
        )
        self.db.commit()
        return self._progress(goal)

    def list_goals(self, account_id: uuid.UUID, limit: int, offset: int) -> Page[GoalResponse]:
        rows, total = self.repo.list_page(account_id, limit, offset)
        return Page(
            items=[self._progress(g) for g in rows], limit=limit, offset=offset, total=total
        )

    def list_active(self, account_id: uuid.UUID, limit: int = 20) -> list[GoalResponse]:
        return [self._progress(g) for g in self.repo.list_active_for_owner(account_id, limit)]

    def change_state(self, account_id: uuid.UUID, goal_id: uuid.UUID, state: str) -> GoalResponse:
        goal = self.repo.get_owned(account_id, goal_id)
        if goal is None:
            raise NotFoundError("Goal not found")
        if goal.state == state:
            return self._progress(goal)
        if state not in TRANSITIONS[goal.state]:
            raise ConflictError("A closed goal cannot be changed")
        goal.state = state
        goal.updated_at = self.clock.utc_now()
        self.audit.record(
            "goal.state_changed",
            entity_type="goal",
            account_id=account_id,
            entity_id=goal.id,
            metadata={"state": state},
        )
        self.db.commit()
        return self._progress(goal)
