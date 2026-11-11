"""ORM models. Importing this package registers every table on Base.metadata."""

from app.models.account import Account, Session
from app.models.alert import AlertAcknowledgement, AlertRule, WellnessAlert
from app.models.connection import Connection, Reading, ReadingProcessingOutcome
from app.models.consent import ConsentRecord, DataRightsRequest
from app.models.goal import Insight, InsightFeedback, WellnessGoal
from app.models.support import AuditLog, SupportRequest

__all__ = [
    "Account",
    "AlertAcknowledgement",
    "AlertRule",
    "AuditLog",
    "ConsentRecord",
    "Connection",
    "DataRightsRequest",
    "Insight",
    "InsightFeedback",
    "Reading",
    "ReadingProcessingOutcome",
    "Session",
    "SupportRequest",
    "WellnessAlert",
    "WellnessGoal",
]
