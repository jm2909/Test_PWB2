from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.clock import utc_now
from app.database import Base
from app.models.types import UTCDateTime


class WellnessGoal(Base):
    __tablename__ = "wellness_goals"
    __table_args__ = (
        CheckConstraint(
            "category IN ('weight_management','fitness','sleep_improvement','general_wellness')",
            name="category",
        ),
        CheckConstraint("target_value > 0", name="target_value"),
        CheckConstraint("state IN ('active','paused','closed')", name="state"),
        Index("ix_goals_account_state", "account_id", "state"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.id"))
    category: Mapped[str] = mapped_column(String(32))
    metric_type: Mapped[str] = mapped_column(String(64))
    target_value: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    target_unit: Mapped[str] = mapped_column(String(32))
    target_date: Mapped[date] = mapped_column(Date)
    state: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now, onupdate=utc_now)


class Insight(Base):
    __tablename__ = "insights"
    __table_args__ = (Index("ix_insights_account_created", "account_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.id"))
    metric_type: Mapped[str] = mapped_column(String(64))
    observation_period_start: Mapped[datetime] = mapped_column(UTCDateTime)
    observation_period_end: Mapped[datetime] = mapped_column(UTCDateTime)
    observation: Mapped[str] = mapped_column(String(1000))
    wellness_guidance: Mapped[str] = mapped_column(String(1000))
    uncertainty: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)


class InsightFeedback(Base):
    __tablename__ = "insight_feedback"
    __table_args__ = (
        UniqueConstraint("insight_id", "account_id", name="uq_insight_feedback_owner"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    insight_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("insights.id"))
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.id"))
    useful: Mapped[bool] = mapped_column(Boolean)
    submitted_at: Mapped[datetime] = mapped_column(UTCDateTime)
