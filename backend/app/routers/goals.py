from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.common_schemas import ErrorResponse
from app.schemas.goal_schemas import GoalCreate, GoalListResponse, GoalResponse
from app.services.goal_service import GoalService, InvalidGoalError

router = APIRouter(tags=["goals"])


@router.post(
    "/goals",
    response_model=GoalResponse,
    status_code=201,
    responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def create_goal(
    payload: GoalCreate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalResponse:
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    try:
        row = GoalService(db).create(user.id, payload, correlation_id)
    except InvalidGoalError as exc:
        raise HTTPException(status_code=422, detail=exc.guidance) from exc
    return GoalResponse.model_validate(row)


@router.get("/goals", response_model=GoalListResponse, responses={401: {"model": ErrorResponse}})
def list_goals(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> GoalListResponse:
    items = [GoalResponse.model_validate(g) for g in GoalService(db).list_active(user.id)]
    return GoalListResponse(items=items, total=len(items))
