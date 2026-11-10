from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.common_schemas import ErrorResponse
from app.schemas.trend_schemas import TrendResponse
from app.services.trend_service import TrendExplanationService, UnsupportedMetricError

router = APIRouter(tags=["trends"])


@router.get("/trends", response_model=TrendResponse, responses={401: {"model": ErrorResponse}})
def get_trend(
    metric_type: Annotated[str, Query()],
    period_days: Annotated[int, Query(ge=7, le=365)],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrendResponse:
    try:
        return TrendExplanationService(db).trend(user.id, metric_type, period_days)
    except UnsupportedMetricError as exc:
        raise HTTPException(
            status_code=422,
            detail="metric_type must be one of weight, body_fat, sleep_duration, resting_heart_rate, steps.",
        ) from exc
