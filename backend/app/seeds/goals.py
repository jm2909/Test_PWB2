"""Seed goals: asha's weight-loss target of 65 kg."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.goal_repository import GoalRepository
from app.seeds import register
from app.seeds.users import user_id


@register("goals", order=36)
def seed_goals(db: Session) -> None:
    repo = GoalRepository(db)
    asha = user_id(db, "asha")
    if repo.get_active(asha, "weight_loss") is None:
        repo.save_active(asha, "weight_loss", Decimal(65), "kg")
