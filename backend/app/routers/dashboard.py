"""Dashboard router: HTTP mapping only."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.clock import Clock
from app.deps import CurrentUser, get_clock, get_current_user, get_db
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import DashboardCompositionService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse, openapi_extra={"x-requirement": "FR-011"})
def get_dashboard(
    user: CurrentUser = Depends(get_current_user),
    db: DbSession = Depends(get_db),
    clock: Clock = Depends(get_clock),
) -> DashboardResponse:
    return DashboardCompositionService(db, clock).compose(user.account_id)
