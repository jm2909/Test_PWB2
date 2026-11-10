from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.common_schemas import ErrorResponse
from app.schemas.consent_schemas import ConsentCreate, ConsentListResponse, ConsentResponse
from app.services.consent_service import ConsentLedgerService

router = APIRouter(tags=["consents"])


@router.post(
    "/consents",
    response_model=ConsentResponse,
    status_code=201,
    responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def record_consent(
    payload: ConsentCreate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConsentResponse:
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    row = ConsentLedgerService(db).record(
        user.id, payload.purpose, payload.version, payload.status, correlation_id
    )
    return ConsentResponse.model_validate(row)


@router.get("/consents", response_model=ConsentListResponse, responses={401: {"model": ErrorResponse}})
def list_consents(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ConsentListResponse:
    history, latest = ConsentLedgerService(db).list_for_user(user.id)
    return ConsentListResponse(
        items=[ConsentResponse.model_validate(r) for r in history],
        total=len(history),
        latest=[ConsentResponse.model_validate(r) for r in latest],
    )
