"""Model factories. Use these instead of constructing models by hand in tests."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from functools import lru_cache
from typing import Any

import bcrypt
from sqlalchemy.orm import Session

from app.models import (
    Alert,
    AuditLog,
    AuthSession,
    ConsentRecord,
    DeviationEvent,
    DeviceConnection,
    Goal,
    Insight,
    OnboardingProgress,
    Recommendation,
    SyncAttempt,
    User,
    WellnessReading,
)

SEED_EMAIL = "asha.menon@example.com"
SEED_PASSWORD = "correct-horse-battery"  # noqa: S105 - documented demo credential


@lru_cache
def hash_for_tests(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def _save(db: Session, obj: Any) -> Any:
    db.add(obj)
    db.commit()
    return obj


def make_user(db: Session, email: str | None = None, password: str = "Test-pass-1", **kw: Any) -> User:
    email = email or f"user-{uuid.uuid4().hex[:8]}@example.com"
    return _save(db, User(email=email, password_hash=hash_for_tests(password), **kw))


def make_session(db: Session, user: User, **kw: Any) -> AuthSession:
    now = datetime.now(UTC)
    values: dict[str, Any] = {
        "token_hash": uuid.uuid4().hex + uuid.uuid4().hex,
        "issued_at": now,
        "expires_at": now + timedelta(minutes=30),
        "last_activity_at": now,
    }
    values.update(kw)
    return _save(db, AuthSession(user_id=user.id, **values))


def make_onboarding(db: Session, user: User, **kw: Any) -> OnboardingProgress:
    values: dict[str, Any] = {
        "profile_json": {"age_range": "30-39"},
        "goal_intent": "weight_loss",
        "device_next_step": "scale",
        "status": "in_progress",
    }
    values.update(kw)
    return _save(db, OnboardingProgress(user_id=user.id, **values))


def make_consent(db: Session, user: User, **kw: Any) -> ConsentRecord:
    values: dict[str, Any] = {
        "purpose": "device_processing",
        "version": "v1",
        "status": "accepted",
        "recorded_at": datetime.now(UTC),
    }
    values.update(kw)
    return _save(db, ConsentRecord(user_id=user.id, **values))


def make_connection(db: Session, user: User, **kw: Any) -> DeviceConnection:
    values: dict[str, Any] = {
        "provider": "sapphire_scale",
        "status": "connected",
        "permitted_categories": ["weight"],
    }
    values.update(kw)
    return _save(db, DeviceConnection(user_id=user.id, **values))


def make_sync_attempt(db: Session, connection: DeviceConnection, **kw: Any) -> SyncAttempt:
    values: dict[str, Any] = {
        "idempotency_key": uuid.uuid4().hex,
        "status": "started",
        "started_at": datetime.now(UTC),
    }
    values.update(kw)
    return _save(db, SyncAttempt(device_connection_id=connection.id, **values))


def make_reading(db: Session, user: User, connection: DeviceConnection, **kw: Any) -> WellnessReading:
    now = datetime.now(UTC)
    values: dict[str, Any] = {
        "source_event_id": uuid.uuid4().hex,
        "metric_type": "weight",
        "value_numeric": Decimal("70.5"),
        "unit": "kg",
        "observed_at": now,
        "normalized_at": now,
    }
    values.update(kw)
    return _save(db, WellnessReading(user_id=user.id, device_connection_id=connection.id, **values))


def make_insight(db: Session, user: User, **kw: Any) -> Insight:
    values: dict[str, Any] = {"status": "published", "evidence_summary": "Based on 7 readings."}
    values.update(kw)
    return _save(db, Insight(user_id=user.id, **values))


def make_deviation(db: Session, user: User, reading: WellnessReading, **kw: Any) -> DeviationEvent:
    values: dict[str, Any] = {"criterion_code": "weight_change_7d", "trend_name": "Weight trend"}
    values.update(kw)
    return _save(db, DeviationEvent(user_id=user.id, wellness_reading_id=reading.id, **values))


def make_alert(db: Session, user: User, deviation: DeviationEvent, **kw: Any) -> Alert:
    values: dict[str, Any] = {
        "urgency": "routine",
        "recommended_next_action": "Keep tracking your weight this week.",
    }
    values.update(kw)
    return _save(db, Alert(user_id=user.id, deviation_event_id=deviation.id, **values))


def make_recommendation(db: Session, user: User, insight: Insight, **kw: Any) -> Recommendation:
    values: dict[str, Any] = {
        "action_text": "Take a short walk daily.",
        "reason_text": "Your activity trend is lower this week.",
    }
    values.update(kw)
    return _save(db, Recommendation(user_id=user.id, insight_id=insight.id, **values))


def make_goal(db: Session, user: User, **kw: Any) -> Goal:
    values: dict[str, Any] = {
        "goal_type": "weight_loss",
        "target_value": Decimal("65"),
        "target_unit": "kg",
        "status": "active",
    }
    values.update(kw)
    return _save(db, Goal(user_id=user.id, **values))


def make_audit(db: Session, user: User | None = None, **kw: Any) -> AuditLog:
    values: dict[str, Any] = {
        "action": "account.created",
        "outcome": "success",
        "severity": "info",
        "correlation_id": uuid.uuid4().hex,
    }
    values.update(kw)
    return _save(db, AuditLog(user_id=user.id if user else None, **values))
