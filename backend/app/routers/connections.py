"""Connections router: HTTP mapping only (FR-006)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.orm import Session as DbSession

from app.clock import Clock
from app.database import get_db
from app.deps import CurrentUser, get_clock, get_current_user
from app.schemas.common import Page, PageParams
from app.schemas.connection import (
    AuthorizationResponse,
    CallbackRequest,
    ConnectionResponse,
    ProviderResponse,
    ScaleConnectRequest,
)
from app.schemas.trend import ConnectionStatusResponse
from app.services.connection import ConnectionService

router = APIRouter(prefix="/connections", tags=["Connections"])


def get_connection_service(
    db: DbSession = Depends(get_db), clock: Clock = Depends(get_clock)
) -> ConnectionService:
    return ConnectionService(db, clock)


@router.post(
    "/scale",
    response_model=ConnectionResponse,
    status_code=201,
    responses={202: {"model": ConnectionResponse}, 403: {"description": "Consent required"}},
    openapi_extra={"x-requirement": "FR-006"},
)
def connect_scale(
    body: ScaleConnectRequest,
    response: Response,
    user: CurrentUser = Depends(get_current_user),
    service: ConnectionService = Depends(get_connection_service),
    idempotency_key: str | None = Header(default=None, max_length=128, alias="Idempotency-Key"),
) -> ConnectionResponse:
    outcome = service.link_scale(user.account_id, body, idempotency_key)
    response.status_code = outcome.status_code
    return outcome.response


@router.get(
    "",
    response_model=Page[ConnectionStatusResponse],
    openapi_extra={"x-requirement": "FR-009"},
)
def list_connections(
    page: PageParams = Depends(),
    user: CurrentUser = Depends(get_current_user),
    service: ConnectionService = Depends(get_connection_service),
) -> Page[ConnectionStatusResponse]:
    return service.list_status(user.account_id, page.limit, page.offset)


@router.get(
    "/providers",
    response_model=list[ProviderResponse],
    openapi_extra={"x-requirement": "FR-007"},
)
def list_providers(
    _user: CurrentUser = Depends(get_current_user),
    service: ConnectionService = Depends(get_connection_service),
) -> list[ProviderResponse]:
    return service.list_providers()


@router.post(
    "/wearables/{provider}/authorizations",
    response_model=AuthorizationResponse,
    status_code=201,
    responses={403: {"description": "Consent required"}, 404: {"description": "Unsupported"}},
    openapi_extra={"x-requirement": "FR-007"},
)
def begin_wearable_authorization(
    provider: str,
    user: CurrentUser = Depends(get_current_user),
    service: ConnectionService = Depends(get_connection_service),
) -> AuthorizationResponse:
    return service.begin_wearable_authorization(user.account_id, provider)


@router.post(
    "/wearables/{provider}/callbacks",
    response_model=ConnectionResponse,
    openapi_extra={"x-requirement": "FR-007"},
)
def complete_wearable_authorization(
    provider: str,
    body: CallbackRequest,
    user: CurrentUser = Depends(get_current_user),
    service: ConnectionService = Depends(get_connection_service),
) -> ConnectionResponse:
    return service.complete_wearable_authorization(user.account_id, provider, body)
