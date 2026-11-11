"""Trends router: HTTP mapping only (FR-012)."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DbSession

from app.clock import Clock
from app.database import get_db
from app.deps import CurrentUser, get_clock, get_current_user
from app.schemas.trend import TrendResponse
from app.services.trend import TrendService

router = APIRouter(prefix="/trends", tags=["Trends"])


@router.get(
    "/{metric_type}",
    response_model=TrendResponse,
    responses={404: {"description": "Unsupported metric"}},
    openapi_extra={"x-requirement": "FR-012"},
)
def get_trend(
    metric_type: str,
    range_: Literal["7d", "30d", "90d", "365d"] = Query("30d", alias="range"),
    user: CurrentUser = Depends(get_current_user),
    db: DbSession = Depends(get_db),
    clock: Clock = Depends(get_clock),
) -> TrendResponse:
    return TrendService(db, clock).trend(user.account_id, metric_type, range_)
