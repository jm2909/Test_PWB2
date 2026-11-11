"""Readings router: HTTP mapping only (FR-008)."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Header, Query, Response
from sqlalchemy.orm import Session as DbSession

from app.clock import Clock
from app.database import get_db
from app.deps import CurrentUser, get_clock, get_current_user
from app.schemas.common import Page, PageParams
from app.schemas.reading import ReadingRequest, ReadingResponse
from app.services.reading import ReadingService

router = APIRouter(prefix="/readings", tags=["Readings"])


def get_reading_service(
    db: DbSession = Depends(get_db), clock: Clock = Depends(get_clock)
) -> ReadingService:
    return ReadingService(db, clock)


@router.post(
    "",
    response_model=ReadingResponse,
    status_code=201,
    responses={200: {"model": ReadingResponse}, 409: {"description": "Key reuse mismatch"}},
    openapi_extra={"x-requirement": "FR-008"},
)
def create_reading(
    body: ReadingRequest,
    response: Response,
    user: CurrentUser = Depends(get_current_user),
    service: ReadingService = Depends(get_reading_service),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> ReadingResponse:
    result = service.ingest(user.account_id, body, idempotency_key)
    if not result.created:
        response.status_code = 200
    return result.reading


@router.get(
    "",
    response_model=Page[ReadingResponse],
    openapi_extra={"x-requirement": "FR-008"},
)
def list_readings(
    metric_type: str | None = Query(default=None, max_length=64),
    from_: datetime | None = Query(default=None, alias="from"),
    to: datetime | None = Query(default=None),
    page: PageParams = Depends(),
    user: CurrentUser = Depends(get_current_user),
    service: ReadingService = Depends(get_reading_service),
) -> Page[ReadingResponse]:
    return service.list_readings(user.account_id, metric_type, from_, to, page.limit, page.offset)
