from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.common_schemas import ErrorResponse
from app.schemas.onboarding_schemas import OnboardingResponse, OnboardingUpdate
from app.services.onboarding_service import OnboardingService

router = APIRouter(tags=["onboarding"])


@router.get("/onboarding", response_model=OnboardingResponse, responses={401: {"model": ErrorResponse}})
def get_onboarding(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> OnboardingResponse:
    return OnboardingService(db).get(user.id)


@router.put("/onboarding", response_model=OnboardingResponse, responses={401: {"model": ErrorResponse}})
def put_onboarding(
    payload: OnboardingUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> OnboardingResponse:
    return OnboardingService(db).save(user.id, payload.profile, payload.goal_intent, payload.device_next_step)
