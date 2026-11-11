BODY = {"email": "Fresh@Example.com", "password": "A-long-password-1", "display_name": "Fresh"}


def test_register_then_login(client):
    r = client.post("/api/v1/auth/accounts", json=BODY)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["email"] == "fresh@example.com"
    assert data["next_step"] == "consent_setup"
    assert "password" not in data and "password_hash" not in data
    assert "A-long-password-1" not in r.text
    login = client.post(
        "/api/v1/auth/tokens", json={"email": "fresh@example.com", "password": BODY["password"]}
    )
    assert login.status_code == 201


def test_duplicate_email_400(client):
    assert client.post("/api/v1/auth/accounts", json=BODY).status_code == 201
    r = client.post("/api/v1/auth/accounts", json={**BODY, "email": "fresh@example.com"})
    assert r.status_code == 400
    assert "detail" in r.json()


def test_invalid_body_422_does_not_echo_password(client):
    r = client.post("/api/v1/auth/accounts", json={**BODY, "password": "Qz9-tiny"})
    assert r.status_code == 422
    assert "Qz9-tiny" not in r.text
    bad_email = {**BODY, "email": "bad"}
    assert client.post("/api/v1/auth/accounts", json=bad_email).status_code == 422
    blank = {**BODY, "display_name": " "}
    assert client.post("/api/v1/auth/accounts", json=blank).status_code == 422


def test_password_never_logged(client, caplog):
    with caplog.at_level("DEBUG"):
        client.post("/api/v1/auth/accounts", json=BODY)
    assert "A-long-password-1" not in caplog.text
