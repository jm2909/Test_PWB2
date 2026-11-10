from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.common_schemas import ErrorResponse
from app.schemas.dashboard_schemas import DashboardResponse
from app.services.dashboard_service import DashboardCompositionService

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse, responses={401: {"model": ErrorResponse}})
def get_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DashboardResponse:
    return DashboardCompositionService(db).compose(user.id)
