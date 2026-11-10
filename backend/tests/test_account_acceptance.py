"""FR-001 acceptance criteria."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditLog, User

URL = "/api/v1/accounts"


def test_valid_registration_creates_account(client: TestClient, db_session: Session) -> None:
    response = client.post(URL, json={"email": "fresh@example.com", "password": "long-enough-pass"})
    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], int)
    assert body["email"] == "fresh@example.com"
    assert body["onboarding_status"]
    assert "password" not in body and "password_hash" not in body
    assert db_session.scalar(select(User).where(User.email == "fresh@example.com")) is not None
    assert db_session.scalar(select(AuditLog).where(AuditLog.action == "account.created")) is not None


def test_duplicate_email_is_409_with_clear_error(client: TestClient) -> None:
    payload = {"email": "twice@example.com", "password": "long-enough-pass"}
    assert client.post(URL, json=payload).status_code == 201
    response = client.post(URL, json=payload)
    assert response.status_code == 409
    assert response.json()["detail"]


def test_invalid_fields_are_422_and_do_not_echo_values(client: TestClient) -> None:
    short = client.post(URL, json={"email": "a@example.com", "password": "short"})
    assert short.status_code == 422
    assert "short" not in short.text.replace("shorter", "")
    assert client.post(URL, json={"email": "not-an-email", "password": "long-enough-pass"}).status_code == 422
    assert client.post(URL, json={"password": "long-enough-pass"}).status_code == 422
