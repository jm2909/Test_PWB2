"""Simulated Sapphire smart-scale pairing. authorization_code "fail" simulates a pairing failure."""

from collections.abc import Sequence
from datetime import datetime

from app.adapters.base import ConnectResult, RawReading, RetryableAdapterError, simulated_readings
from app.adapters.wearable_base import raise_simulated_fault

FAIL_CODE = "fail"


class SapphireScaleAdapter:
    provider: str = "sapphire_scale"
    supported_modes: tuple[str, ...] = ("pair",)

    def connect(self, authorization_code: str | None) -> ConnectResult:
        if authorization_code == FAIL_CODE:
            raise RetryableAdapterError("We couldn't pair your scale. Check it is on and nearby.")
        return ConnectResult(permitted_categories=["weight", "body_fat"])

    def fetch_readings(
        self, categories: Sequence[str], now: datetime, simulate: str | None = None
    ) -> list[RawReading]:
        raise_simulated_fault(simulate)
        return simulated_readings(self.provider, categories, now)
