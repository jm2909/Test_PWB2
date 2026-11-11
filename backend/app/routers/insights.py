"""Insights router: HTTP mapping only (FR-013)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.clock import Clock
from app.database import get_db
from app.deps import CurrentUser, get_clock, get_current_user
from app.schemas.common import Page, PageParams
from app.schemas.insight import FeedbackRequest, FeedbackResponse, InsightResponse
from app.services.insight import InsightService

router = APIRouter(prefix="/insights", tags=["Dashboard, trends, and insights"])


def get_insight_service(
    db: DbSession = Depends(get_db), clock: Clock = Depends(get_clock)
) -> InsightService:
    return InsightService(db, clock)


@router.get("", response_model=Page[InsightResponse], openapi_extra={"x-requirement": "FR-013"})
def list_insights(
    page: PageParams = Depends(),
    user: CurrentUser = Depends(get_current_user),
    service: InsightService = Depends(get_insight_service),
) -> Page[InsightResponse]:
    return service.list_insights(user.account_id, page.limit, page.offset)


@router.post(
    "/{insight_id}/feedback",
    response_model=FeedbackResponse,
    status_code=201,
    openapi_extra={"x-requirement": "FR-013"},
)
def submit_feedback(
    insight_id: uuid.UUID,
    body: FeedbackRequest,
    user: CurrentUser = Depends(get_current_user),
    service: InsightService = Depends(get_insight_service),
) -> FeedbackResponse:
    return service.submit_feedback(user.account_id, insight_id, body.useful)
