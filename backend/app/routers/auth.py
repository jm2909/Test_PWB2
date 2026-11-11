"""Authentication router: HTTP mapping only."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from app.deps import CurrentUser, get_auth_service, get_current_user, login_rate_limit
from app.schemas.auth import AccountResponse, LoginRequest, RegisterRequest, TokenResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication and account"])


@router.post(
    "/tokens",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(login_rate_limit)],
    openapi_extra={"x-requirement": "FR-002"},
)
def create_token(
    body: LoginRequest, service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    return service.login(body)


@router.delete(
    "/tokens/current",
    status_code=status.HTTP_204_NO_CONTENT,
    openapi_extra={"x-requirement": "FR-002"},
)
def revoke_current_token(
    user: CurrentUser = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> Response:
    service.logout(user.account_id, user.session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(login_rate_limit)],
    openapi_extra={"x-requirement": "FR-001"},
)
def register_account(
    body: RegisterRequest, service: AuthService = Depends(get_auth_service)
) -> AccountResponse:
    return service.register(body)
