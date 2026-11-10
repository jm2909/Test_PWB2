from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.common_schemas import ErrorResponse
from app.schemas.insight_schemas import InsightListResponse, InsightResponse
from app.services.consent_service import ProcessingBlockedError
from app.services.insight_service import InsightService

router = APIRouter(tags=["insights"])


@router.post(
    "/insights",
    response_model=InsightResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def generate_insight(
    request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> InsightResponse:
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    try:
        row = InsightService(db).generate(user.id, correlation_id)
    except ProcessingBlockedError as exc:
        raise HTTPException(status_code=403, detail=exc.explanation) from exc
    return _to_response(
        row.id, row.status, row.observed_trend, row.wellness_implication, row.suppression_reason
    )


@router.get("/insights", response_model=InsightListResponse, responses={401: {"model": ErrorResponse}})
def list_insights(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InsightListResponse:
    rows, total = InsightService(db).list_for_user(user.id, limit, offset)
    items = [
        _to_response(r.id, r.status, r.observed_trend, r.wellness_implication, r.suppression_reason)
        for r in rows
    ]
    return InsightListResponse(items=items, total=total)


def _to_response(
    insight_id: object, status: str, trend: str | None, implication: str | None, reason: str | None
) -> InsightResponse:
    """Suppressed results carry id=null in the POST contract; stored rows keep their id for listing."""
    return InsightResponse.model_validate(
        {
            "id": insight_id,
            "status": status,
            "observed_trend": trend,
            "wellness_implication": implication,
            "suppression_reason": reason,
        }
    )
