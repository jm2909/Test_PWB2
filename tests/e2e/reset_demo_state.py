"""E2E helper: put asha's alerts and insight feedback back to the seeded state (run from backend/)."""
from sqlalchemy import delete

from app import database
from app.models import Account, AlertAcknowledgement, InsightFeedback, WellnessAlert
from app.seeds.alerts import seed_insights_and_alerts
from app.seeds.goals import seed_acknowledged_alert
from app.seeds.accounts import seed_accounts

with database.SessionLocal() as db:
    accounts = seed_accounts(db)
    asha = accounts["asha"].id
    db.execute(delete(AlertAcknowledgement).where(AlertAcknowledgement.account_id == asha))
    db.execute(delete(InsightFeedback).where(InsightFeedback.account_id == asha))
    db.execute(delete(WellnessAlert).where(WellnessAlert.account_id == asha))
    db.flush()
    seed_insights_and_alerts(db, accounts)
    seed_acknowledged_alert(db, accounts)
    db.commit()
