import pytest
from sqlalchemy.orm import Session

from app.adapters.registry import build_registry
from app.schemas.device_schemas import DeviceConnectionCreate
from app.seeds.users import user_id
from app.services.device_service import DeviceService


def req(provider: str, code: str | None = None) -> DeviceConnectionCreate:
    return DeviceConnectionCreate.model_validate(
        {"provider": provider, "connection_mode": "authorize", "authorization_code": code}
    )


def test_registry_categories() -> None:
    reg = build_registry()
    assert reg["wearable_platform_a"].connect(None).permitted_categories == [
        "sleep",
        "heart_rate",
        "activity",
    ]
    assert reg["wearable_platform_b"].connect("ok").permitted_categories == [
        "sleep",
        "heart_rate",
        "activity",
        "weight",
    ]
    assert reg["wearable_platform_c"].supported_modes == ("authorize",)


@pytest.mark.parametrize(
    ("code", "status", "action"),
    [
        ("ok", "connected", None),
        (None, "connected", None),
        ("revoke", "revoked", "Reconnect"),
        ("fail", "failed", "Try again"),
    ],
)
def test_authorize_outcomes(seeded: Session, code: str | None, status: str, action: str | None) -> None:
    row = DeviceService(seeded).connect(user_id(seeded, "asha"), req("wearable_platform_c", code), "c")
    assert row.status == status and row.recovery_action == action
    assert (row.failure_reason is None) == (status == "connected")


def test_reconnect_restores_connected(seeded: Session) -> None:
    svc = DeviceService(seeded)
    uid = user_id(seeded, "asha")
    assert svc.connect(uid, req("wearable_platform_c", "revoke"), "c").status == "revoked"
    row = svc.connect(uid, req("wearable_platform_c", "ok"), "c")
    assert row.status == "connected" and row.failure_reason is None and row.recovery_action is None
    assert len([r for r in svc.list_for_user(uid) if r.provider == "wearable_platform_c"]) == 1
