"""Unified dashboard (FR-013): composes stored readings, goals and connections. Database only."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.database import utcnow
from app.models import Goal, WellnessReading
from app.repositories.alert_repository import AlertRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.onboarding_repository import OnboardingRepository
from app.repositories.reading_repository import ReadingRepository
from app.schemas.dashboard_schemas import DashboardResponse, SignalGroup, SourceGap
from app.schemas.goal_schemas import GoalResponse

LOOKBACK_DAYS = 30
NO_GOAL = "No goal set"
GAP_TEXT: dict[str, tuple[str, str, str, str]] = {
    # group -> (title, reason, recovery action, link)
    "body_composition": (
        "Body composition",
        "Your smart scale has not synced weight readings.",
        "Check scale connection",
        "/devices",
    ),
    "sleep": (
        "Sleep",
        "Your wearable has not synced sleep readings.",
        "Check wearable connection",
        "/devices",
    ),
    "heart_rate": (
        "Heart rate",
        "Your wearable has not synced heart rate readings.",
        "Check wearable connection",
        "/devices",
    ),
    "activity": (
        "Activity",
        "Your wearable has not synced activity readings.",
        "Check wearable connection",
        "/devices",
    ),
}


def _values(rows: list[WellnessReading]) -> list[float]:
    return [float(r.value_numeric) for r in rows]


def _avg(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 1) if values else None


class DashboardCompositionService:
    def __init__(self, db: Session) -> None:
        self.readings = ReadingRepository(db)
        self.goals = GoalRepository(db)
        self.devices = DeviceRepository(db)
        self.onboarding = OnboardingRepository(db)
        self.alerts = AlertRepository(db)

    def compose(self, user_id: int) -> DashboardResponse:
        now = utcnow()
        by_metric: dict[str, list[WellnessReading]] = {}
        for row in self.readings.list_since(user_id, now - timedelta(days=LOOKBACK_DAYS)):
            by_metric.setdefault(row.metric_type, []).append(row)
        week_ago = now - timedelta(days=7)

        def last7(metric: str) -> list[WellnessReading]:
            return [r for r in by_metric.get(metric, []) if r.observed_at >= week_ago]

        built = {
            "body_composition": self._body(by_metric),
            "sleep": self._sleep(by_metric, last7("sleep_hours")),
            "heart_rate": self._heart(by_metric, last7("resting_heart_rate")),
            "activity": self._activity(by_metric, last7("steps"), now),
        }
        groups: list[SignalGroup] = []
        gaps: list[SourceGap] = []
        for key, group in built.items():
            if group is not None:
                groups.append(group)
                continue
            title, reason, action, link = GAP_TEXT[key]
            gaps.append(
                SourceGap(key=key, group=key, title=title, reason=reason, recovery_action=action, link=link)
            )
        goals = self.goals.list_active(user_id)
        if goals:
            groups.append(self._goal_signal(goals[0], by_metric, last7("sleep_hours")))
        else:
            gaps.append(
                SourceGap(
                    key="goals",
                    group="goal_signals",
                    title="Goals",
                    reason=NO_GOAL,
                    recovery_action="Set a goal",
                    link="/goals",
                )
            )
        return DashboardResponse(
            display_name=self._display_name(user_id),
            last_synced_at=self._last_synced(user_id),
            signal_groups=groups,
            source_gaps=gaps,
            active_goals=[GoalResponse.model_validate(g) for g in goals],
            unread_alert_count=self.alerts.count_unread(user_id),
        )

    def _display_name(self, user_id: int) -> str:
        row = self.onboarding.get(user_id)
        name = row.profile_json.get("display_name") if row else None
        return str(name) if name else "there"

    def _last_synced(self, user_id: int) -> datetime | None:
        times = [
            c.last_successful_sync_at
            for c in self.devices.list_for_user(user_id)
            if c.last_successful_sync_at
        ]
        return max(times) if times else None

    def _body(self, by_metric: dict[str, list[WellnessReading]]) -> SignalGroup | None:
        weights = by_metric.get("weight", [])
        fats = by_metric.get("body_fat", [])
        if not weights and not fats:
            return None
        details: list[str] = []
        metrics: dict[str, float | None] = {
            "weight_kg": None,
            "body_fat_percent": None,
            "weight_delta_kg": None,
        }
        if weights:
            latest = weights[-1]
            metrics["weight_kg"] = round(float(latest.value_numeric), 1)
            prior = [r for r in weights if r.observed_at <= latest.observed_at - timedelta(days=7)]
            if prior:
                delta = round(float(latest.value_numeric) - float(prior[-1].value_numeric), 1)
                metrics["weight_delta_kg"] = delta
                details.append(f"{delta:+.1f} kg vs last week")
        if fats:
            metrics["body_fat_percent"] = round(float(fats[-1].value_numeric), 1)
            details.insert(0, f"Body fat {metrics['body_fat_percent']}%")
        value = metrics["weight_kg"]
        return SignalGroup(
            key="body_composition",
            group="body_composition",
            title="Body composition",
            value=f"{value:.1f}" if value is not None else None,
            unit="kg" if value is not None else None,
            details=details,
            metrics=metrics,
        )

    def _sleep(
        self, by_metric: dict[str, list[WellnessReading]], week: list[WellnessReading]
    ) -> SignalGroup | None:
        rows = by_metric.get("sleep_hours", [])
        if not rows:
            return None
        last = round(float(rows[-1].value_numeric), 1)
        avg = _avg(_values(week))
        details = [f"7-day average {avg} h"] if avg is not None else []
        return SignalGroup(
            key="sleep",
            group="sleep",
            title="Sleep",
            value=f"{last:.1f}",
            unit="h last night",
            details=details,
            metrics={"last_night_hours": last, "avg_7d_hours": avg},
        )

    def _heart(
        self, by_metric: dict[str, list[WellnessReading]], week: list[WellnessReading]
    ) -> SignalGroup | None:
        rows = by_metric.get("resting_heart_rate", [])
        if not rows:
            return None
        latest = round(float(rows[-1].value_numeric))
        values = _values(week)
        low = round(min(values)) if values else None
        high = round(max(values)) if values else None
        details = [f"7-day range {low}–{high} bpm"] if low is not None else []
        return SignalGroup(
            key="heart_rate",
            group="heart_rate",
            title="Heart rate",
            value=str(latest),
            unit="bpm resting",
            details=details,
            metrics={"resting_bpm": float(latest), "range_7d_min": low, "range_7d_max": high},
        )

    def _activity(
        self,
        by_metric: dict[str, list[WellnessReading]],
        week: list[WellnessReading],
        now: datetime,
    ) -> SignalGroup | None:
        rows = by_metric.get("steps", [])
        if not rows:
            return None
        today = [r for r in rows if r.observed_at.date() == now.date()]
        steps_today = round(float(today[-1].value_numeric)) if today else None
        avg = _avg(_values(week))
        details = [f"7-day average {round(avg):,} steps"] if avg is not None else []
        return SignalGroup(
            key="activity",
            group="activity",
            title="Activity",
            value=f"{steps_today:,}" if steps_today is not None else None,
            unit="steps today",
            details=details if steps_today is not None else ["No steps synced today", *details],
            metrics={
                "steps_today": float(steps_today) if steps_today is not None else None,
                "avg_7d_steps": avg,
            },
        )

    def _goal_signal(
        self, goal: Goal, by_metric: dict[str, list[WellnessReading]], sleep_week: list[WellnessReading]
    ) -> SignalGroup:
        target = float(goal.target_value)
        current: float | None = None
        if goal.goal_type in ("weight_loss", "muscle_gain") and by_metric.get("weight"):
            current = round(float(by_metric["weight"][-1].value_numeric), 1)
        elif goal.goal_type == "sleep_improvement":
            current = _avg(_values(sleep_week))
        details = [f"Target {target:g} {goal.target_unit}"]
        if current is None:
            details.append("No current value yet")
        return SignalGroup(
            key="goals",
            group="goal_signals",
            title="Goal",
            value=f"{current:g}" if current is not None else None,
            unit=goal.target_unit if current is not None else None,
            details=details,
            metrics={"current": current, "target": target},
        )
