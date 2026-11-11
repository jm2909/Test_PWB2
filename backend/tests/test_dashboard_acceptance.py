from tests.conftest import Factories


def test_requires_auth(client):
    assert client.get("/api/v1/dashboard").status_code == 401


def test_asha_dashboard_from_seed(client, db_session, auth_headers):
    from app.seeds.accounts import seed_accounts
    from app.seeds.readings import seed_readings

    accounts = seed_accounts(db_session)
    seed_readings(db_session, accounts)
    seed_readings(db_session, accounts)  # idempotent
    db_session.commit()
    r = client.get("/api/v1/dashboard", headers=auth_headers("asha"))
    assert r.status_code == 200, r.text
    body = r.json()
    assert {m["metric_type"] for m in body["measurements"]} == {
        "weight",
        "steps",
        "sleep_duration",
        "active_minutes",
    }
    for m in body["measurements"]:
        assert m["source"] and m["captured_at"] and m["status"] == "current"
    assert body["unavailable_categories"] == []
    assert len(body["source_statuses"]) == 2
    assert body["alerts"] == [] and body["goals"] == []


def test_rohan_all_unavailable(client, db_session, auth_headers):
    from app.seeds.accounts import seed_accounts
    from app.seeds.readings import seed_readings

    seed_readings(db_session, seed_accounts(db_session))
    db_session.commit()
    body = client.get("/api/v1/dashboard", headers=auth_headers("rohan")).json()
    assert body["measurements"] == []
    assert len(body["unavailable_categories"]) == 4
    assert all(u["status"] == "unavailable" for u in body["unavailable_categories"])


def test_owner_isolation(client, db_session, auth_headers):
    f = Factories(db_session)
    headers = auth_headers("asha")
    other = f.account()
    f.reading(other, metric_type="steps", value=99999, unit="count")
    f.goal(other)
    body = client.get("/api/v1/dashboard", headers=headers).json()
    assert body["measurements"] == [] and body["goals"] == []
