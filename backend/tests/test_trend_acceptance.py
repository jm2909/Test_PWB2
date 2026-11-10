import pytest
from fastapi.testclient import TestClient


def test_trends_require_auth(client: TestClient) -> None:
    assert (
        client.get("/api/v1/trends", params={"metric_type": "weight", "period_days": 30}).status_code == 401
    )


def test_ac1_chronological_trend(auth_client: TestClient) -> None:
    response = auth_client.get("/api/v1/trends", params={"metric_type": "weight", "period_days": 30})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "available" and body["explanation"]
    stamps = [p["observed_at"] for p in body["points"]]
    assert stamps == sorted(stamps) and len(stamps) > 1


def test_ac2_insufficient_history_message(auth_client: TestClient) -> None:
    body = auth_client.get("/api/v1/trends", params={"metric_type": "steps", "period_days": 365}).json()
    assert body["status"] == "insufficient_history"
    assert "A reliable trend is not available yet." in body["explanation"]


@pytest.mark.parametrize(
    "params",
    [
        {"metric_type": "weight", "period_days": 6},
        {"metric_type": "weight", "period_days": 366},
        {"metric_type": "weight", "period_days": "x"},
        {"metric_type": "bogus", "period_days": 30},
        {"period_days": 30},
        {"metric_type": "weight"},
    ],
)
def test_invalid_query_is_422(auth_client: TestClient, params: dict[str, object]) -> None:
    assert auth_client.get("/api/v1/trends", params=params).status_code == 422
