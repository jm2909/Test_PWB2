from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.repositories.deviation_repository import DeviationRepository
from app.schemas.common_schemas import ErrorResponse
from app.schemas.deviation_schemas import DeviationEventListResponse, DeviationEventResponse

router = APIRouter(tags=["deviation-events"])


@router.get(
    "/deviation-events",
    response_model=DeviationEventListResponse,
    responses={401: {"model": ErrorResponse}},
)
def list_deviation_events(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeviationEventListResponse:
    rows, total = DeviationRepository(db).list_for_user(user.id, limit, offset)
    return DeviationEventListResponse(
        items=[DeviationEventResponse.model_validate(r) for r in rows], total=total
    )
