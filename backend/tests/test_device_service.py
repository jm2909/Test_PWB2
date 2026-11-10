import pytest
from sqlalchemy.orm import Session

from app.adapters.base import ConnectResult, NonRetryableAdapterError
from app.schemas.device_schemas import DeviceConnectionCreate
from app.seeds.users import user_id
from app.services.consent_service import ProcessingBlockedError
from app.services.device_service import DeviceService, UnsupportedConnectionError


class SpyAdapter:
    provider: str = "sapphire_scale"
    supported_modes: tuple[str, ...] = ("pair",)

    def __init__(self, error: Exception | None = None) -> None:
        self.calls = 0
        self.error = error

    def connect(self, authorization_code: str | None) -> ConnectResult:
        self.calls += 1
        if self.error:
            raise self.error
        return ConnectResult(["weight"])


def req(
    code: str | None = None, provider: str = "sapphire_scale", mode: str = "pair"
) -> DeviceConnectionCreate:
    return DeviceConnectionCreate.model_validate(
        {"provider": provider, "connection_mode": mode, "authorization_code": code}
    )


def test_consent_gate_never_calls_adapter(seeded: Session) -> None:
    spy = SpyAdapter()
    svc = DeviceService(seeded, {"sapphire_scale": spy})
    for persona in ("meena", "rohan"):
        with pytest.raises(ProcessingBlockedError):
            svc.connect(user_id(seeded, persona), req(), "c")
    assert spy.calls == 0


def test_success_upserts_single_row(seeded: Session) -> None:
    svc = DeviceService(seeded)
    uid = user_id(seeded, "asha")
    row = svc.connect(uid, req(), "c")
    assert row.status == "connected" and row.permitted_categories == ["weight", "body_fat"]
    svc.connect(uid, req("fail"), "c")
    rows = [r for r in svc.list_for_user(uid) if r.provider == "sapphire_scale"]
    assert len(rows) == 1 and rows[0].status == "failed" and rows[0].recovery_action == "Try again"
    svc.connect(uid, req(), "c")
    again = [r for r in svc.list_for_user(uid) if r.provider == "sapphire_scale"]
    assert again[0].status == "connected" and again[0].failure_reason is None


def test_non_retryable_is_action_required(seeded: Session) -> None:
    svc = DeviceService(seeded, {"sapphire_scale": SpyAdapter(NonRetryableAdapterError("Access revoked"))})
    row = svc.connect(user_id(seeded, "asha"), req(), "c")
    assert row.status == "action_required" and row.failure_reason == "Access revoked" and row.recovery_action


def test_unsupported_mode_and_provider(seeded: Session) -> None:
    svc = DeviceService(seeded)
    uid = user_id(seeded, "asha")
    with pytest.raises(UnsupportedConnectionError):
        svc.connect(uid, req(mode="authorize"), "c")
    with pytest.raises(UnsupportedConnectionError):
        svc.connect(uid, req(provider="wearable_platform_a", mode="pair"), "c")
