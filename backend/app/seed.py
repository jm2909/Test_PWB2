"""Idempotent seed orchestrator: python -m app.seed"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app import database
from app.logging_config import configure_logging
from app.seeds.accounts import seed_accounts
from app.seeds.alerts import seed_insights_and_alerts
from app.seeds.connections import seed_scale_connections
from app.seeds.consents import seed_consents
from app.seeds.data_rights import seed_data_rights
from app.seeds.goals import seed_acknowledged_alert, seed_goals
from app.seeds.readings import seed_readings
from app.seeds.support import seed_support
from app.seeds.wearables import seed_wearables

logger = logging.getLogger("app.seed")


def seed_all(db: Session) -> None:
    accounts = seed_accounts(db)
    seed_consents(db, accounts)
    seed_readings(db, accounts)
    seed_scale_connections(db, accounts)
    seed_wearables(db, accounts)
    seed_data_rights(db, accounts)
    seed_insights_and_alerts(db, accounts)
    seed_acknowledged_alert(db, accounts)
    seed_goals(db, accounts)
    seed_support(db, accounts)
    db.commit()


def run_seed() -> None:
    with database.SessionLocal() as db:
        seed_all(db)
    logger.info("Seed complete")


if __name__ == "__main__":
    configure_logging()
    run_seed()
    print("Seed complete")
