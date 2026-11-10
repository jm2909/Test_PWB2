from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.seeds.users import user_id
from tests.conftest import issue_headers
from tests.factories import make_consent, make_insight, make_user

URL = "/api/v1/insights"


def test_requires_auth(client: TestClient) -> None:
    assert client.post(URL).status_code == 401
    assert client.get(URL).status_code == 401
    assert client.get(URL, headers={"Authorization": "Bearer junk"}).status_code == 401


def test_revoked_and_inactive_sessions_rejected(client: TestClient, seeded: Session) -> None:
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import select

    from app.models import AuthSession

    headers = issue_headers(seeded, user_id(seeded, "asha"))
    assert client.get(URL, headers=headers).status_code == 200
    row = seeded.scalar(select(AuthSession))
    assert row is not None
    row.last_activity_at = datetime.now(UTC) - timedelta(hours=2)
    seeded.commit()
    assert client.get(URL, headers=headers).status_code == 401
    row.last_activity_at = datetime.now(UTC)
    row.revoked_at = datetime.now(UTC)
    seeded.commit()
    assert client.get(URL, headers=headers).status_code == 401


def test_seeded_asha_publishes_sleep_insight(
    client: TestClient, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    response = client.post(URL, headers=persona_headers("asha"))
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "published"
    assert "sleep" in body["observed_trend"].lower()
    assert body["wellness_implication"]


def test_seeded_meena_is_suppressed(
    client: TestClient, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    body = client.post(URL, headers=persona_headers("meena")).json()
    assert body["status"] == "suppressed"
    assert body["observed_trend"] is None and body["suppression_reason"]


def test_declined_consent_is_403_with_explanation(client: TestClient, db_session: Session) -> None:
    user = make_user(db_session)
    make_consent(db_session, user, purpose="personalized_insights", status="declined")
    response = client.post(URL, headers=issue_headers(db_session, user.id))
    assert response.status_code == 403
    assert response.json()["detail"]


def test_list_is_owner_scoped_and_paginated(client: TestClient, db_session: Session) -> None:
    mine, other = make_user(db_session), make_user(db_session)
    for _ in range(3):
        make_insight(db_session, mine)
    make_insight(db_session, other)
    headers = issue_headers(db_session, mine.id)
    body = client.get(URL, headers=headers).json()
    assert body["total"] == 3 and len(body["items"]) == 3
    page = client.get(URL, params={"limit": 2, "offset": 2}, headers=headers).json()
    assert page["total"] == 3 and len(page["items"]) == 1
    assert client.get(URL, params={"limit": 0}, headers=headers).status_code == 422
    assert client.get(URL, params={"limit": 101}, headers=headers).status_code == 422
    assert client.get(URL, params={"offset": -1}, headers=headers).status_code == 422
