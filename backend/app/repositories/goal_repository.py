from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import utcnow
from app.models import Goal


class GoalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active(self, user_id: int) -> list[Goal]:
        return list(
            self.db.scalars(
                select(Goal)
                .where(Goal.user_id == user_id, Goal.status == "active")
                .order_by(Goal.updated_at.desc(), Goal.goal_type)
            )
        )

    def get_active(self, user_id: int, goal_type: str) -> Goal | None:
        return self.db.scalar(
            select(Goal).where(Goal.user_id == user_id, Goal.goal_type == goal_type, Goal.status == "active")
        )

    def save_active(self, user_id: int, goal_type: str, value: Decimal, unit: str) -> Goal:
        """One active goal per type: a newer target replaces the existing one."""
        row = self.get_active(user_id, goal_type)
        if row is None:
            row = Goal(user_id=user_id, goal_type=goal_type, status="active")
            self.db.add(row)
        row.target_value = value
        row.target_unit = unit
        row.updated_at = utcnow()
        self.db.flush()
        return row
