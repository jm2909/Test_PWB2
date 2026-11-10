from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.alert_schemas import AlertListResponse
from app.schemas.common_schemas import ErrorResponse
from app.services.alert_service import SafeAlertPresentationService

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=AlertListResponse, responses={401: {"model": ErrorResponse}})
def list_alerts(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AlertListResponse:
    correlation_id = str(getattr(request.state, "correlation_id", "unknown"))
    items, total = SafeAlertPresentationService(db).list_for_user(user.id, limit, offset, correlation_id)
    return AlertListResponse(items=items, total=total)
