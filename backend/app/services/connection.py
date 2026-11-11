"""ConnectionService: link a Sapphire scale behind the consent gate (FR-006)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from app.adapters.base import (
    AdapterAuthorizationDenied,
    AdapterPayloadInvalid,
    AdapterUnavailable,
    ConnectionResult,
    ScaleAdapter,
    WearableAdapter,
)
from app.adapters.simulated import SimulatedScaleAdapter, SimulatedWearableAdapter
from app.clock import Clock, SystemClock
from app.config import get_settings
from app.errors import NotFoundError
from app.models import Connection
from app.repositories.connection import ConnectionRepository
from app.schemas.common import Page
from app.schemas.connection import (
    AuthorizationResponse,
    CallbackRequest,
    ConnectionResponse,
    ProviderResponse,
    ScaleConnectRequest,
)
from app.schemas.trend import ConnectionStatusResponse
from app.services.audit import AuditService
from app.services.consent import ConsentService
from app.services.freshness import effective_status, recovery_action_for

FAILURE_MESSAGE = "Connection could not be completed. Retry or contact support."
RECOVERY_ACTION = "retry_or_contact_support"
FAILURE_CODE = "link_failed"
WEARABLE_RECOVERY_ACTION = "retry_or_disconnect"
WEARABLE_FAILURE_MESSAGE = "Authorization was not completed. Retry or disconnect this source."
WEARABLE_NOT_SUPPORTED = "Wearable provider is not supported"
AUTHORIZATION_TTL = timedelta(minutes=10)


@dataclass(frozen=True)
class LinkOutcome:
    response: ConnectionResponse
    status_code: int


def _to_response(conn: Connection) -> ConnectionResponse:
    failed = conn.status == "failed"
    return ConnectionResponse(
        id=conn.id,
        source=conn.source,
        external_identifier=conn.external_identifier,
        status=conn.status,
        last_successful_sync_at=conn.last_successful_sync_at,
        recovery_action=(
            (WEARABLE_RECOVERY_ACTION if conn.source == "wearable" else RECOVERY_ACTION)
            if failed
            else None
        ),
        message=(
            (WEARABLE_FAILURE_MESSAGE if conn.source == "wearable" else FAILURE_MESSAGE)
            if failed
            else None
        ),
        provider=conn.provider,
        authorization_state=conn.authorization_state,
    )


class ConnectionService:
    def __init__(
        self,
        db: DbSession,
        clock: Clock | None = None,
        scale_adapter: ScaleAdapter | None = None,
        wearable_adapter: WearableAdapter | None = None,
    ) -> None:
        self.db = db
        self.clock = clock or SystemClock()
        self.adapter: ScaleAdapter = scale_adapter or SimulatedScaleAdapter()
        self.wearables: WearableAdapter = wearable_adapter or SimulatedWearableAdapter(self.clock)
        self.repo = ConnectionRepository(db)
        self.consent = ConsentService(db, self.clock)
        self.audit = AuditService(db, self.clock)

    def list_status(
        self, account_id: uuid.UUID, limit: int, offset: int
    ) -> Page[ConnectionStatusResponse]:
        """Owner-only page with server-computed freshness and recovery actions (FR-009)."""
        now = self.clock.utc_now()
        stale_after = timedelta(hours=get_settings().freshness_stale_after_hours)
        rows, total = self.repo.list_active_page(account_id, limit, offset)
        items = []
        for conn in rows:
            status = effective_status(conn.status, conn.last_successful_sync_at, now, stale_after)
            items.append(
                ConnectionStatusResponse(
                    id=conn.id,
                    source=conn.source,
                    provider=conn.provider,
                    display_label=conn.display_label,
                    status=status,
                    last_successful_sync_at=conn.last_successful_sync_at,
                    recovery_action=recovery_action_for(status, conn.source),
                )
            )
        return Page[ConnectionStatusResponse](items=items, limit=limit, offset=offset, total=total)

    def link_scale(
        self,
        account_id: uuid.UUID,
        command: ScaleConnectRequest,
        idempotency_key: str | None = None,  # duplicates are already collapsed by uniqueness
    ) -> LinkOutcome:
        self.consent.require_active(account_id)
        provider = getattr(self.adapter, "provider", "sapphire-scale")
        existing = self.repo.find_one(account_id, "scale", provider, command.device_identifier)
        if existing is not None and existing.status != "failed":
            return LinkOutcome(_to_response(existing), 200)

        result: ConnectionResult | None
        try:
            result = self.adapter.link(account_id, command.device_identifier)
        except (AdapterUnavailable, AdapterAuthorizationDenied, AdapterPayloadInvalid):
            result = None

        now = self.clock.utc_now()
        conn = existing
        if conn is None:
            conn = Connection(
                account_id=account_id,
                source="scale",
                provider=provider,
                external_identifier=command.device_identifier,
                display_label=command.device_label,
                authorization_state="pending",
                status="pending",
            )
        if result is None:
            conn.authorization_state = "failed"
            conn.status = "failed"
            conn.last_failure_code = FAILURE_CODE
        else:
            conn.authorization_state = result.authorization_state
            conn.status = result.status
            conn.last_failure_code = None
            if result.status == "current":
                conn.last_successful_sync_at = now
        conn.display_label = command.device_label
        try:
            self.repo.add(conn)
        except IntegrityError:
            self.db.rollback()
            raced = self.repo.find_one(account_id, "scale", provider, command.device_identifier)
            if raced is None:
                raise
            return LinkOutcome(_to_response(raced), 200)
        self.audit.record(
            "connection.scale_link",
            entity_type="connection",
            account_id=account_id,
            entity_id=conn.id,
            severity="warning" if conn.status == "failed" else "info",
            metadata={"status": conn.status, "source": "scale"},
        )
        self.db.commit()
        code = {"pending": 202, "failed": 200}.get(conn.status, 201)
        return LinkOutcome(_to_response(conn), code)

    # ---- wearable flows (FR-007) -------------------------------------------------------
    def list_providers(self) -> list[ProviderResponse]:
        return [
            ProviderResponse(
                provider=name,
                display_name=name.replace("-", " ").title(),
                authorization_mode="oauth_redirect",
            )
            for name in get_settings().wearable_provider_list
        ]

    @staticmethod
    def _normalise_provider(provider: str) -> str:
        name = provider.strip().lower()
        if name not in get_settings().wearable_provider_list:
            raise NotFoundError(WEARABLE_NOT_SUPPORTED)
        return name

    def begin_wearable_authorization(
        self, account_id: uuid.UUID, provider: str
    ) -> AuthorizationResponse:
        name = self._normalise_provider(provider)
        self.consent.require_active(account_id)
        try:
            start = self.wearables.begin_authorization(account_id, name)
        except AdapterUnavailable as exc:
            raise NotFoundError(WEARABLE_NOT_SUPPORTED) from exc
        rows = self.repo.list_provider_rows(account_id, name)
        # Reuse a retryable row first so retries never pile up duplicates.
        order = {"failed": 0, "pending": 1, "authorized": 2}
        rows.sort(key=lambda r: order.get(r.authorization_state, 3))
        now = self.clock.utc_now()
        conn = rows[0] if rows else None
        if conn is None:
            conn = Connection(
                account_id=account_id,
                source="wearable",
                provider=name,
                external_identifier=f"{name}-pending-{uuid.uuid4().hex[:12]}",
                display_label=name.replace("-", " ").title(),
                authorization_state="pending",
                status="pending",
            )
        elif conn.authorization_state in ("failed", "revoked"):
            conn.authorization_state = "pending"
            conn.status = "pending"
            conn.last_failure_code = None
        self.repo.add(conn)
        self.audit.record(
            "connection.wearable_authorization_started",
            entity_type="connection",
            account_id=account_id,
            entity_id=conn.id,
            metadata={"provider": name},
        )
        self.db.commit()
        return AuthorizationResponse(
            connection_id=conn.id,
            authorization_url=start.authorization_url,
            expires_at=now + AUTHORIZATION_TTL,
        )

    def complete_wearable_authorization(
        self, account_id: uuid.UUID, provider: str, command: CallbackRequest
    ) -> ConnectionResponse:
        name = self._normalise_provider(provider)
        conn = self.repo.get_owned(account_id, command.connection_id)
        if conn is None or conn.source != "wearable" or conn.provider != name:
            raise NotFoundError("Connection not found")
        callback = {
            "state": command.state,
            "code": command.code,
            "error": command.error,
            "account_id": str(account_id),
        }
        try:
            result = self.wearables.complete_authorization(name, callback)
        except (AdapterUnavailable, AdapterAuthorizationDenied, AdapterPayloadInvalid):
            conn.authorization_state = "failed"
            conn.status = "failed"
            conn.last_failure_code = "authorization_failed"
        else:
            twin = self.repo.find_one(account_id, "wearable", name, result.external_identifier)
            if twin is not None and twin.id != conn.id:
                # Already linked under this identifier: keep one association per source.
                twin.authorization_state = result.authorization_state
                twin.status = (
                    "pending" if twin.status in ("failed", "disconnected") else twin.status
                )
                twin.last_failure_code = None
                self.db.delete(conn)
                conn = twin
            else:
                conn.external_identifier = result.external_identifier
                conn.display_label = result.display_label
                conn.authorization_state = result.authorization_state
                conn.status = result.status
                conn.last_failure_code = None
        self.audit.record(
            "connection.wearable_authorization_completed",
            entity_type="connection",
            account_id=account_id,
            entity_id=conn.id,
            severity="warning" if conn.status == "failed" else "info",
            metadata={"provider": name, "status": conn.status},
        )
        self.db.commit()
        return _to_response(conn)
