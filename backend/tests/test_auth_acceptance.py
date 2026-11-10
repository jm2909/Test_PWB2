from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AuthSession
from tests.conftest import login
from tests.factories import SEED_EMAIL, SEED_PASSWORD

URL = "/api/v1/auth/sessions"


def test_valid_login_reaches_protected_content(client: TestClient, seeded: Session) -> None:
    response = client.post(URL, json={"email": SEED_EMAIL, "password": SEED_PASSWORD})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer" and body["expires_at"]
    assert body["user"]["email"] == SEED_EMAIL and body["user"]["onboarding_status"] == "complete"
    me = client.get("/api/v1/insights", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200


@pytest.mark.parametrize(
    "email,password", [(SEED_EMAIL, "wrong-password"), ("nobody@example.com", "whatever-password")]
)
def test_invalid_credentials_generic_401(
    client: TestClient, seeded: Session, email: str, password: str
) -> None:
    response = client.post(URL, json={"email": email, "password": password})
    assert response.status_code == 401
    assert "access_token" not in response.text
    assert client.get("/api/v1/insights").status_code == 401


def test_empty_password_is_422(client: TestClient) -> None:
    assert client.post(URL, json={"email": SEED_EMAIL, "password": ""}).status_code == 422


@pytest.fixture
def limited(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("LOGIN_RATE_LIMIT", "3/minute")
    get_settings.cache_clear()
    yield
    monkeypatch.undo()
    get_settings.cache_clear()


def test_rate_limit_returns_429(client: TestClient, seeded: Session, limited: None) -> None:
    codes = [
        client.post(URL, json={"email": SEED_EMAIL, "password": "bad-password"}).status_code for _ in range(4)
    ]
    assert codes == [401, 401, 401, 429]
    last = client.post(URL, json={"email": SEED_EMAIL, "password": SEED_PASSWORD})
    assert last.status_code == 429 and last.json()["detail"] == "Too many attempts. Try again later."


def test_logout_revokes_token(client: TestClient, seeded: Session) -> None:
    headers = login(client)
    assert client.delete(f"{URL}/current", headers=headers).status_code == 204
    assert client.get("/api/v1/insights", headers=headers).status_code == 401
    assert client.delete(f"{URL}/current", headers=headers).status_code == 401


def test_logout_requires_auth(client: TestClient) -> None:
    assert client.delete(f"{URL}/current").status_code == 401


def test_expired_session_rejected(client: TestClient, seeded: Session) -> None:
    headers = login(client)
    row = seeded.query(AuthSession).one()
    row.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    seeded.commit()
    assert client.get("/api/v1/insights", headers=headers).status_code == 401


def test_inactive_session_rejected(client: TestClient, seeded: Session) -> None:
    headers = login(client)
    row = seeded.query(AuthSession).one()
    row.last_activity_at = datetime.now(UTC) - timedelta(
        minutes=get_settings().session_inactivity_minutes + 1
    )
    seeded.commit()
    assert client.get("/api/v1/insights", headers=headers).status_code == 401
