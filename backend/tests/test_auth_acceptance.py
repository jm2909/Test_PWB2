from __future__ import annotations

from app.seeds.constants import DEMO_ACCOUNTS
from tests.conftest import login


def test_valid_signin_opens_protected_area(client, seeded_accounts):
    headers = login(client, "asha")
    assert client.get("/api/v1/dashboard", headers=headers).status_code == 200


def test_invalid_signin_does_not_reveal_account(client, seeded_accounts):
    unknown = client.post(
        "/api/v1/auth/tokens", json={"email": "ghost@example.com", "password": "Wrong-pass-12345"}
    )
    wrong = client.post(
        "/api/v1/auth/tokens",
        json={"email": DEMO_ACCOUNTS["asha"]["email"], "password": "Wrong-pass-12345"},
    )
    assert unknown.status_code == wrong.status_code == 401
    assert unknown.json() == wrong.json() == {"detail": "Invalid credentials"}


def test_signout_revokes_token(client, seeded_accounts):
    headers = login(client, "asha")
    assert client.delete("/api/v1/auth/tokens/current", headers=headers).status_code == 204
    again = client.delete("/api/v1/auth/tokens/current", headers=headers)
    assert again.status_code == 401
    assert again.json() == {"detail": "Session is not active"}
    assert client.get("/api/v1/dashboard", headers=headers).status_code == 401


def test_signout_requires_token(client):
    assert client.delete("/api/v1/auth/tokens/current").status_code == 401


def test_login_rate_limited(client, seeded_accounts, monkeypatch):
    from app.config import get_settings

    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("LOGIN_RATE_LIMIT", "2/minute")
    get_settings.cache_clear()
    try:
        body = {"email": "ghost@example.com", "password": "Wrong-pass-12345"}
        codes = [client.post("/api/v1/auth/tokens", json=body).status_code for _ in range(3)]
        assert codes == [401, 401, 429]
    finally:
        monkeypatch.undo()
        get_settings.cache_clear()
