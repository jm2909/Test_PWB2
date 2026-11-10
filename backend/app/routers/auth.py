from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.account_schemas import AccountResponse
from app.schemas.auth_schemas import LoginRequest, SessionResponse
from app.schemas.common_schemas import ErrorResponse
from app.services.auth_service import AuthService, InvalidCredentialsError
from app.services.onboarding_service import OnboardingService
from app.services.rate_limiter import login_limiter

router = APIRouter(tags=["auth"])
_bearer = HTTPBearer(auto_error=False)


def _correlation_id(request: Request) -> str:
    return str(getattr(request.state, "correlation_id", "unknown"))


@router.post(
    "/auth/sessions",
    response_model=SessionResponse,
    responses={401: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
)
def create_session(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> SessionResponse:
    settings = get_settings()
    client_ip = request.client.host if request.client else "unknown"
    if settings.rate_limit_enabled and not login_limiter.hit(client_ip, settings.login_rate_limit):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")
    try:
        result = AuthService(db).login(payload.email, payload.password, _correlation_id(request))
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=401, detail="Invalid email or password.", headers={"WWW-Authenticate": "Bearer"}
        ) from exc
    return SessionResponse(
        access_token=result.token,
        token_type="bearer",  # noqa: S106 - token scheme name, not a secret
        expires_at=result.expires_at,
        user=AccountResponse(
            id=result.user.id,
            email=result.user.email,
            onboarding_status=OnboardingService(db).status(result.user.id),
        ),
    )


@router.delete(
    "/auth/sessions/current",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"model": ErrorResponse}},
)
def delete_current_session(
    request: Request,
    user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Response:
    if credentials is not None:
        AuthService(db).logout(credentials.credentials, user.id, _correlation_id(request))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
