from datetime import datetime

from pydantic import BaseModel

from app.schemas.goal_schemas import GoalResponse


class SignalGroup(BaseModel):
    key: str
    group: str
    title: str
    value: str | None
    unit: str | None
    details: list[str]
    metrics: dict[str, float | None]


class SourceGap(BaseModel):
    key: str
    group: str
    title: str
    reason: str
    recovery_action: str | None
    link: str | None


class DashboardResponse(BaseModel):
    display_name: str
    last_synced_at: datetime | None
    signal_groups: list[SignalGroup]
    source_gaps: list[SourceGap]
    active_goals: list[GoalResponse]
    unread_alert_count: int
