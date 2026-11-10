from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.common_schemas import ErrorResponse
from app.schemas.explanation_schemas import MetricExplanationRequest, MetricExplanationResponse
from app.services.explanation_service import TrendExplanationService
from app.services.trend_service import UnsupportedMetricError

router = APIRouter(tags=["metric-explanations"])


@router.post(
    "/metric-explanations",
    response_model=MetricExplanationResponse,
    responses={401: {"model": ErrorResponse}},
)
def explain_metric(
    payload: MetricExplanationRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MetricExplanationResponse:
    try:
        return TrendExplanationService(db).explain(user.id, payload.metric_type, payload.period_days)
    except UnsupportedMetricError as exc:
        raise HTTPException(
            status_code=422,
            detail="metric_type must be one of weight, body_fat, sleep_duration, resting_heart_rate, steps.",
        ) from exc
