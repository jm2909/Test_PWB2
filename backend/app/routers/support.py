"""Support router: HTTP mapping only (FR-023)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.clock import Clock
from app.database import get_db
from app.deps import CurrentUser, get_clock, get_current_user
from app.schemas.support import SupportRequestCreate, SupportRequestResponse
from app.services.support import SupportService

router = APIRouter(prefix="/support-requests", tags=["Support"])


def get_support_service(
    db: DbSession = Depends(get_db), clock: Clock = Depends(get_clock)
) -> SupportService:
    return SupportService(db, clock)


@router.post(
    "",
    status_code=201,
    response_model=SupportRequestResponse,
    openapi_extra={"x-requirement": "FR-023"},
)
def create_support_request(
    body: SupportRequestCreate,
    user: CurrentUser = Depends(get_current_user),
    service: SupportService = Depends(get_support_service),
) -> SupportRequestResponse:
    return service.submit(user.account_id, body)
