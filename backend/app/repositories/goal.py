from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from app.models import WellnessGoal


class GoalRepository:
    def __init__(self, db: DbSession) -> None:
        self.db = db

    def list_active_for_owner(self, account_id: uuid.UUID, limit: int = 20) -> list[WellnessGoal]:
        return list(
            self.db.scalars(
                select(WellnessGoal)
                .where(WellnessGoal.account_id == account_id, WellnessGoal.state == "active")
                .order_by(WellnessGoal.target_date, WellnessGoal.id)
                .limit(limit)
            )
        )

    def list_page(
        self, account_id: uuid.UUID, limit: int, offset: int
    ) -> tuple[list[WellnessGoal], int]:
        total = self.db.scalar(
            select(func.count())
            .select_from(WellnessGoal)
            .where(WellnessGoal.account_id == account_id)
        )
        rows = self.db.scalars(
            select(WellnessGoal)
            .where(WellnessGoal.account_id == account_id)
            .order_by(WellnessGoal.target_date, WellnessGoal.id)
            .limit(limit)
            .offset(offset)
        )
        return list(rows), int(total or 0)

    def get_owned(self, account_id: uuid.UUID, goal_id: uuid.UUID) -> WellnessGoal | None:
        return self.db.scalar(
            select(WellnessGoal).where(
                WellnessGoal.id == goal_id, WellnessGoal.account_id == account_id
            )
        )

    def add(self, goal: WellnessGoal) -> WellnessGoal:
        self.db.add(goal)
        self.db.flush()
        return goal
