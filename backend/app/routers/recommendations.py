from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.common_schemas import ErrorResponse
from app.schemas.recommendation_schemas import RecommendationResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter(tags=["recommendations"])


@router.get(
    "/recommendations",
    response_model=RecommendationResponse,
    responses={401: {"model": ErrorResponse}},
)
def get_recommendations(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> RecommendationResponse:
    return RecommendationService(db).select(user.id)
