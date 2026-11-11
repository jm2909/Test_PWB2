"""Deterministic simulated providers (no real provider API is specified)."""

from __future__ import annotations

import hashlib
import hmac
import uuid
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from app.adapters.base import (
    AdapterAuthorizationDenied,
    AdapterPayloadInvalid,
    AdapterUnavailable,
    AuthorizationStart,
    ConnectionResult,
    NormalizedReading,
)
from app.clock import Clock, SystemClock, ensure_utc
from app.config import get_settings


class SimulatedScaleAdapter:
    provider = "sapphire-scale"

    def link(self, account_id: uuid.UUID, device_identifier: str) -> ConnectionResult:
        ident = device_identifier.strip()
        if not ident:
            raise AdapterPayloadInvalid("device identifier required")
        if ident.upper().startswith("UNAVAILABLE"):
            raise AdapterUnavailable("scale unreachable")
        upper = ident.upper()
        if "FAIL" in upper:
            raise AdapterUnavailable("scale link failed")
        return ConnectionResult(
            provider=self.provider,
            external_identifier=ident,
            display_label=f"Sapphire Scale ...{ident[-4:]}",
            authorization_state="pending" if "PENDING" in upper else "authorized",
            status="pending" if "PENDING" in upper else "current",
        )

    def normalize(self, payload: dict[str, Any]) -> NormalizedReading:
        try:
            captured = ensure_utc(datetime.fromisoformat(str(payload["captured_at"])))
            return NormalizedReading(
                metric_type=str(payload["metric_type"]),
                value=Decimal(str(payload["value"])),
                unit=str(payload["unit"]),
                captured_at=captured,
                source="scale",
                provider_event_id=str(payload["provider_event_id"]),
                connection_external_id=payload.get("device_identifier"),
            )
        except (KeyError, ValueError, InvalidOperation) as exc:
            raise AdapterPayloadInvalid("payload not recognised") from exc


class SimulatedWearableAdapter:
    def __init__(self, clock: Clock | None = None, providers: list[str] | None = None) -> None:
        self.clock = clock or SystemClock()
        configured = get_settings().wearable_provider_list
        self.providers = providers if providers is not None else configured

    def _check(self, provider: str) -> None:
        if provider.lower() not in self.providers:
            raise AdapterUnavailable("provider not enabled")

    @staticmethod
    def _sign(account_id: uuid.UUID | str, provider: str) -> str:
        key = get_settings().jwt_secret_key.encode()
        msg = f"{account_id}:{provider.lower()}".encode()
        return hmac.new(key, msg, hashlib.sha256).hexdigest()[:40]

    def begin_authorization(self, account_id: uuid.UUID, provider: str) -> AuthorizationStart:
        self._check(provider)
        state = self._sign(account_id, provider)
        return AuthorizationStart(
            provider=provider.lower(),
            authorization_url=f"/simulated-providers/{provider.lower()}/authorize?state={state}",
            state=state,
        )

    def complete_authorization(self, provider: str, callback: dict[str, Any]) -> ConnectionResult:
        self._check(provider)
        if callback.get("error") or str(callback.get("code", "")).lower() == "denied":
            raise AdapterAuthorizationDenied("authorization denied")
        state = str(callback.get("state", ""))
        if not state:
            raise AdapterPayloadInvalid("state required")
        expected = self._sign(str(callback.get("account_id", "")), provider)
        if not hmac.compare_digest(state, expected):
            raise AdapterPayloadInvalid("state not valid")
        return ConnectionResult(
            provider=provider.lower(),
            external_identifier=f"{provider.lower()}-{state[:12]}",
            display_label=f"{provider.title()} wearable",
            authorization_state="authorized",
            status="pending",
        )

    def sync(self, connection: ConnectionResult) -> list[NormalizedReading]:
        now = self.clock.utc_now().replace(minute=0, second=0, microsecond=0)
        out: list[NormalizedReading] = []
        for metric, value, unit in (
            ("steps", "8200", "count"),
            ("resting_heart_rate", "64", "bpm"),
            ("sleep_duration", "7.2", "hours"),
        ):
            stamp = now - timedelta(hours=1)
            out.append(
                NormalizedReading(
                    metric_type=metric,
                    value=Decimal(value),
                    unit=unit,
                    captured_at=stamp,
                    source="wearable",
                    provider_event_id=f"{connection.external_identifier}:{metric}:{stamp:%Y%m%d%H}",
                    connection_external_id=connection.external_identifier,
                )
            )
        return out
