import jwt
import pytest
from sqlalchemy import select

from app.config import get_settings
from app.models import AuditLog
from app.models import Session as SessionModel
from app.security import hash_token
from tests.conftest import login


def test_health(client):
    assert client.get("/health").status_code == 200
    assert client.get("/health/ready").status_code == 200
    assert "X-Correlation-ID" in client.get("/health").headers
    assert client.get("/health").headers["X-Content-Type-Options"] == "nosniff"


def test_login_through_real_endpoint(client, seeded_accounts, db_session):
    headers = login(client, "asha")
    token = headers["Authorization"].split()[1]
    claims = jwt.decode(token, get_settings().jwt_secret_key, algorithms=["HS256"])
    assert "exp" in claims
    stored = db_session.scalar(select(SessionModel))
    assert stored.token_hash == hash_token(token) and stored.token_hash != token


def test_login_response_shape(client, seeded_accounts):
    r = client.post(
        "/api/v1/auth/tokens",
        json={"email": "asha@sapphire.example", "password": "Wellness-Demo-2026!"},
    )
    body = r.json()
    assert r.status_code == 201
    assert set(body) == {"access_token", "token_type", "expires_at", "account"}
    assert "password_hash" not in body["account"]


@pytest.mark.parametrize(
    "email,password",
    [
        ("asha@sapphire.example", "wrong-password-123"),
        ("nobody@sapphire.example", "wrong-password-123"),
    ],
)
def test_failed_login_is_uniform(client, seeded_accounts, db_session, email, password):
    r = client.post("/api/v1/auth/tokens", json={"email": email, "password": password})
    assert r.status_code == 401
    assert r.json() == {"detail": "Invalid credentials"}
    logs = db_session.scalars(select(AuditLog)).all()
    assert logs and all("password" not in str(a.event_metadata) for a in logs)


def test_short_password_rejected_without_echo(client):
    r = client.post("/api/v1/auth/tokens", json={"email": "a@b.co", "password": "short"})
    assert r.status_code == 422
    assert "short" not in r.text.replace("too_short", "").replace("String should", "")


def test_rate_limit(client, seeded_accounts, monkeypatch):
    monkeypatch.setenv("X", "1")
    settings = get_settings()
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(settings, "login_rate_limit", "2/minute")
    codes = [
        client.post(
            "/api/v1/auth/tokens",
            json={"email": "asha@sapphire.example", "password": "wrong-password-123"},
        ).status_code
        for _ in range(3)
    ]
    assert codes == [401, 401, 429]


def _protected_client(client):
    from fastapi import Depends

    from app.deps import CurrentUser, get_current_user
    from app.main import app

    if not any(getattr(r, "path", None) == "/_whoami" for r in app.routes):

        @app.get("/_whoami", include_in_schema=False)
        def whoami(user: CurrentUser = Depends(get_current_user)) -> dict[str, str]:
            return {"email": user.email}

    return client


def test_get_current_user_paths(client, seeded_accounts, db_session):
    c = _protected_client(client)
    assert c.get("/_whoami").status_code == 401
    assert c.get("/_whoami", headers={"Authorization": "Bearer garbage"}).status_code == 401
    headers = login(c, "asha")
    assert c.get("/_whoami", headers=headers).json() == {"email": "asha@sapphire.example"}
    session = db_session.scalar(select(SessionModel))
    from datetime import UTC, datetime

    session.revoked_at = datetime.now(UTC)
    db_session.commit()
    assert c.get("/_whoami", headers=headers).status_code == 401


def test_factories_build_every_model(factories):
    a = factories.account()
    factories.session(a)
    factories.consent(a)
    factories.rights_request(a)
    conn = factories.connection(a)
    r = factories.reading(a, connection_id=conn.id)
    factories.outcome(a, connection_id=conn.id)
    rule = factories.alert_rule()
    alert = factories.alert(a, rule, r)
    factories.acknowledgement(a, alert)
    factories.goal(a)
    ins = factories.insight(a)
    factories.insight_feedback(a, ins)
    factories.support_request(a)
    factories.audit_log(a)
