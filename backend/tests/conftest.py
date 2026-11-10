# backend/tests/conftest.py - shared by every test file. Extend it; never add a second database setup.
import os
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path

# 1. Configuration BEFORE anything imports the app: the committed dev.env, then test overrides.
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
os.environ["SEED_ON_START"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

import app.models  # noqa: E402, F401 - registers every model on Base before create_all
from app.database import Base, SessionLocal, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402
from tests.factories import SEED_EMAIL, SEED_PASSWORD  # noqa: E402

LOGIN_PATH = "/api/v1/auth/sessions"


@pytest.fixture(autouse=True)
def _fresh_schema() -> Iterator[None]:
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> Iterator[None]:
    from app.services.rate_limiter import login_limiter

    login_limiter.reset()
    yield
    login_limiter.reset()


@pytest.fixture
def db_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def seeded(db_session: Session) -> Session:
    """Run every registered seed (idempotent) so the documented credentials exist."""
    from app.seeds import run_all

    run_all(db_session)
    return db_session


def login(client: TestClient, email: str = SEED_EMAIL, password: str = SEED_PASSWORD) -> dict[str, str]:
    """Sign in through the real endpoint; return the Authorization headers."""
    response = client.post(LOGIN_PATH, json={"email": email, "password": password})
    assert response.status_code in (200, 201), response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def auth_headers(client: TestClient, seeded: Session) -> dict[str, str]:
    return login(client)


@pytest.fixture
def auth_client(client: TestClient, auth_headers: dict[str, str]) -> TestClient:
    client.headers.update(auth_headers)
    return client


def issue_headers(db: Session, user_id: int) -> dict[str, str]:
    """Authorization headers from a real server-side session (no login endpoint needed)."""
    from app.services.session_service import SessionService

    return {"Authorization": f"Bearer {SessionService(db).issue(user_id)}"}


@pytest.fixture
def persona_headers(seeded: Session) -> Callable[[str], dict[str, str]]:
    """persona ('asha'|'rohan'|'meena') -> headers backed by an issued session."""
    from app.seeds.users import user_id

    return lambda persona: issue_headers(seeded, user_id(seeded, persona))
