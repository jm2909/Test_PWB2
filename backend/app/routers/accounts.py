from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.account_schemas import AccountCreate, AccountResponse
from app.schemas.common_schemas import ErrorResponse
from app.services.account_service import ONBOARDING_NOT_STARTED, AccountService, DuplicateEmailError

router = APIRouter(tags=["accounts"])


@router.post(
    "/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
def create_account(
    payload: AccountCreate, request: Request, db: Session = Depends(get_db)
) -> AccountResponse:
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    try:
        user = AccountService(db).register(payload.email, payload.password, correlation_id)
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=409, detail="An account with this email already exists.") from exc
    return AccountResponse(id=user.id, email=user.email, onboarding_status=ONBOARDING_NOT_STARTED)
