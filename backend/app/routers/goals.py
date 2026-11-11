from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.clock import Clock
from app.database import get_db
from app.deps import CurrentUser, get_clock, get_current_user
from app.schemas.common import Page, PageParams
from app.schemas.goal import GoalCreateRequest, GoalResponse, GoalStateRequest
from app.services.goal import GoalService

router = APIRouter(prefix="/goals", tags=["Alerts and goals"])


def get_goal_service(
    db: DbSession = Depends(get_db), clock: Clock = Depends(get_clock)
) -> GoalService:
    return GoalService(db, clock)


@router.post(
    "", response_model=GoalResponse, status_code=201, openapi_extra={"x-requirement": "FR-017"}
)
def create_goal(
    body: GoalCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    service: GoalService = Depends(get_goal_service),
) -> GoalResponse:
    return service.create(user.account_id, body)


@router.get("", response_model=Page[GoalResponse], openapi_extra={"x-requirement": "FR-017"})
def list_goals(
    page: PageParams = Depends(),
    user: CurrentUser = Depends(get_current_user),
    service: GoalService = Depends(get_goal_service),
) -> Page[GoalResponse]:
    return service.list_goals(user.account_id, page.limit, page.offset)


@router.patch("/{goal_id}", response_model=GoalResponse, openapi_extra={"x-requirement": "FR-017"})
def update_goal_state(
    goal_id: uuid.UUID,
    body: GoalStateRequest,
    user: CurrentUser = Depends(get_current_user),
    service: GoalService = Depends(get_goal_service),
) -> GoalResponse:
    return service.change_state(user.account_id, goal_id, body.state)
