"""Consent router: HTTP mapping only."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.deps import CurrentUser, get_consent_service, get_current_user
from app.schemas.consent import ConsentRequest, ConsentResponse
from app.errors import NotFoundError
from app.services.consent import ConsentService

router = APIRouter(prefix="/consents", tags=["Consent"])


@router.get("/current", response_model=ConsentResponse | None, openapi_extra={"x-requirement": "FR-003"})
def get_current_consent(
    user: CurrentUser = Depends(get_current_user),
    service: ConsentService = Depends(get_consent_service),
) -> ConsentResponse | None:
    # No decision yet is a normal state for a new account: 200 with null, not an error.
    try:
        return service.current(user.account_id)
    except NotFoundError:
        return None


@router.put("/current", response_model=ConsentResponse, openapi_extra={"x-requirement": "FR-003"})
def put_current_consent(
    body: ConsentRequest,
    user: CurrentUser = Depends(get_current_user),
    service: ConsentService = Depends(get_consent_service),
) -> ConsentResponse:
    return service.record(user.account_id, body)
