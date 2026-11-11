# Shared by every test file. Extend it; never add a second database setup.
import os
import tempfile
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
for _seed in ("dev.env", ".env.example"):
    if (_BACKEND / _seed).is_file():
        for _line in (_BACKEND / _seed).read_text().splitlines():
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _value = _line.removeprefix("export ").split("=", 1)
                os.environ.setdefault(_key.strip(), _value.strip().strip("\"'"))
        break
_DB_FILE = Path(tempfile.mkdtemp()) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_FILE.as_posix()}"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["SEED_ON_STARTUP"] = "false"
os.environ["ENVIRONMENT"] = "test"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

import app.models  # noqa: E402,F401 - registers every model on Base
from app.database import Base, SessionLocal, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Account  # noqa: E402
from app.ratelimit import login_limiter  # noqa: E402
from app.seeds.accounts import seed_accounts  # noqa: E402
from app.seeds.constants import DEMO_ACCOUNTS  # noqa: E402

TestingSession = SessionLocal


@pytest.fixture(autouse=True)
def _fresh_schema():
    Base.metadata.create_all(engine)  # tests build their own database; the app never does
    login_limiter.reset()
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session() -> Session:
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def seeded_accounts(db_session) -> dict[str, Account]:
    accounts = seed_accounts(db_session)
    db_session.commit()
    return accounts


def login(client: TestClient, persona: str = "asha") -> dict[str, str]:
    """Sign in through the REAL endpoint with the canonical seed credentials."""
    spec = DEMO_ACCOUNTS[persona]
    response = client.post(
        "/api/v1/auth/tokens", json={"email": spec["email"], "password": spec["password"]}
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def auth_headers(client, seeded_accounts):
    def _headers(persona: str = "asha") -> dict[str, str]:
        return login(client, persona)

    return _headers


@pytest.fixture
def auth_client(client, seeded_accounts):
    client.headers.update(login(client, "asha"))
    return client


# ---- model factories (real field names) --------------------------------------------------
def _now() -> datetime:
    return datetime.now(UTC)


class Factories:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _save(self, obj):
        self.db.add(obj)
        self.db.commit()
        return obj

    def account(self, **kw):
        from app.models import Account as M
        from app.security import hash_password

        data = {
            "email": f"user-{uuid.uuid4().hex[:8]}@example.com",
            "password_hash": hash_password("Factory-pass-123"),
            "display_name": "Factory User",
        }
        return self._save(M(**{**data, **kw}))

    def session(self, account, **kw):
        from app.models import Session as M

        now = _now()
        data = {
            "account_id": account.id,
            "token_hash": uuid.uuid4().hex,
            "issued_at": now,
            "expires_at": now + timedelta(hours=1),
            "last_activity_at": now,
        }
        return self._save(M(**{**data, **kw}))

    def consent(self, account, **kw):
        from app.models import ConsentRecord as M

        data = {
            "account_id": account.id,
            "decision": "granted",
            "notice_version": "2026-01",
            "data_categories": ["weight", "activity"],
            "purpose": "wellness_support",
            "recorded_at": _now(),
        }
        return self._save(M(**{**data, **kw}))

    def rights_request(self, account, **kw):
        from app.models import DataRightsRequest as M

        now = _now()
        data = {
            "account_id": account.id,
            "reference": f"DR-{uuid.uuid4().hex[:12]}",
            "request_type": "export",
            "status": "submitted",
            "requested_at": now,
            "fulfillment_due_at": now + timedelta(days=30),
        }
        return self._save(M(**{**data, **kw}))

    def connection(self, account, **kw):
        from app.models import Connection as M

        data = {
            "account_id": account.id,
            "source": "scale",
            "provider": "sapphire-scale",
            "external_identifier": f"SC-{uuid.uuid4().hex[:8]}",
            "display_label": "Bathroom scale",
            "authorization_state": "authorized",
            "status": "current",
        }
        return self._save(M(**{**data, **kw}))

    def reading(self, account, **kw):
        from app.models import Reading as M

        now = _now()
        data = {
            "account_id": account.id,
            "metric_type": "weight",
            "value": 70,
            "unit": "kg",
            "source": "manual",
            "captured_at": now,
            "ingested_at": now,
            "idempotency_key": uuid.uuid4().hex,
        }
        return self._save(M(**{**data, **kw}))

    def outcome(self, account, **kw):
        from app.models import ReadingProcessingOutcome as M

        data = {
            "account_id": account.id,
            "outcome": "accepted",
            "reason_code": "ok",
            "occurred_at": _now(),
        }
        return self._save(M(**{**data, **kw}))

    def alert_rule(self, **kw):
        from app.models import AlertRule as M

        data = {
            "identifier": f"rule-{uuid.uuid4().hex[:8]}",
            "version": "1",
            "metric_type": "weight",
            "definition": {"operator": "gt", "threshold": 100},
            "content_template": "Observed pattern in {metric}.",
            "enabled": True,
        }
        return self._save(M(**{**data, **kw}))

    def alert(self, account, rule, reading, **kw):
        from app.models import WellnessAlert as M

        data = {
            "account_id": account.id,
            "alert_rule_id": rule.id,
            "source_reading_id": reading.id,
            "metric_type": reading.metric_type,
            "event_at": _now(),
            "reason": "Observed pattern.",
            "state": "active",
        }
        return self._save(M(**{**data, **kw}))

    def acknowledgement(self, account, alert, **kw):
        from app.models import AlertAcknowledgement as M

        data = {"alert_id": alert.id, "account_id": account.id, "acknowledged_at": _now()}
        return self._save(M(**{**data, **kw}))

    def goal(self, account, **kw):
        from datetime import date

        from app.models import WellnessGoal as M

        data = {
            "account_id": account.id,
            "category": "weight_management",
            "metric_type": "weight",
            "target_value": 65,
            "target_unit": "kg",
            "target_date": date.today() + timedelta(days=90),
            "state": "active",
        }
        return self._save(M(**{**data, **kw}))

    def insight(self, account, **kw):
        from app.models import Insight as M

        now = _now()
        data = {
            "account_id": account.id,
            "metric_type": "weight",
            "observation_period_start": now - timedelta(days=7),
            "observation_period_end": now,
            "observation": "Your weight readings were steady.",
            "wellness_guidance": "Keep your routine.",
            "uncertainty": "Based on a small number of readings.",
        }
        return self._save(M(**{**data, **kw}))

    def insight_feedback(self, account, insight, **kw):
        from app.models import InsightFeedback as M

        data = {
            "insight_id": insight.id,
            "account_id": account.id,
            "useful": True,
            "submitted_at": _now(),
        }
        return self._save(M(**{**data, **kw}))

    def support_request(self, account, **kw):
        from app.models import SupportRequest as M

        data = {
            "account_id": account.id,
            "reference": f"SR-{uuid.uuid4().hex[:12]}",
            "category": "account",
            "description": "Need help.",
            "context_type": "account",
            "status": "submitted",
            "submitted_at": _now(),
        }
        return self._save(M(**{**data, **kw}))

    def audit_log(self, account=None, **kw):
        from app.models import AuditLog as M

        data = {
            "account_id": account.id if account else None,
            "correlation_id": "test-correlation",
            "event_type": "test.event",
            "severity": "info",
            "entity_type": "test",
            "event_metadata": {},
            "occurred_at": _now(),
        }
        return self._save(M(**{**data, **kw}))


@pytest.fixture
def factories(db_session) -> Factories:
    return Factories(db_session)


@pytest.fixture
def full_seed(db_session, seeded_accounts):
    """Run the whole idempotent seed (consent, readings, connections, data-rights)."""
    from app.seed import seed_all

    seed_all(db_session)
    return seeded_accounts
