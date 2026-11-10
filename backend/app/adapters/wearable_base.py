"""Wearable adapter contract. authorization_code: absent/"ok" connects, "revoke" revokes, "fail" fails."""

from collections.abc import Sequence
from datetime import datetime

from app.adapters.base import (
    ConnectResult,
    NonRetryableAdapterError,
    RawReading,
    RetryableAdapterError,
    simulated_readings,
)

OK_CODE = "ok"
REVOKE_CODE = "revoke"
FAIL_CODE = "fail"


class AuthorizationRevokedError(NonRetryableAdapterError):
    """The provider reports the user's authorization was revoked."""

    recovery_action = "Reconnect"


class PermissionsChangedError(NonRetryableAdapterError):
    """The provider rejected the request because permissions need to be re-granted."""

    recovery_action = "Review permissions"


def raise_simulated_fault(simulate: str | None) -> None:
    """Shared fault simulation: revoke | permission | fail."""
    if simulate == "revoke":
        raise AuthorizationRevokedError("Access was revoked at the provider.")
    if simulate == "permission":
        raise PermissionsChangedError("Permissions need to be updated.")
    if simulate == "fail":
        raise RetryableAdapterError("The provider did not respond.")


class WearableAdapter:
    """Base for simulated wearable providers; subclasses set provider and categories."""

    provider: str = ""
    supported_modes: tuple[str, ...] = ("authorize",)
    categories: tuple[str, ...] = ()

    def connect(self, authorization_code: str | None) -> ConnectResult:
        if authorization_code == REVOKE_CODE:
            raise AuthorizationRevokedError("Access was revoked at the provider.")
        if authorization_code == FAIL_CODE:
            raise RetryableAdapterError("The provider did not respond.")
        return ConnectResult(permitted_categories=list(self.categories))

    def fetch_readings(
        self, categories: Sequence[str], now: datetime, simulate: str | None = None
    ) -> list[RawReading]:
        raise_simulated_fault(simulate)
        return simulated_readings(self.provider, categories, now)
