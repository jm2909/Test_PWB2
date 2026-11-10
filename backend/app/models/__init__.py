"""ORM models. Importing this package registers every table on Base.metadata."""

from app.models.connected import DeviceConnection, SyncAttempt, WellnessReading
from app.models.identity import AuthSession, ConsentRecord, OnboardingProgress, User
from app.models.wellness import Alert, AuditLog, DeviationEvent, Goal, Insight, Recommendation

__all__ = [
    "Alert",
    "AuditLog",
    "AuthSession",
    "ConsentRecord",
    "DeviceConnection",
    "DeviationEvent",
    "Goal",
    "Insight",
    "OnboardingProgress",
    "Recommendation",
    "SyncAttempt",
    "User",
    "WellnessReading",
]
