"""Data-rights router: HTTP mapping only (FR-005)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.clock import Clock
from app.database import get_db
from app.deps import CurrentUser, get_clock, get_current_user
from app.schemas.common import Page, PageParams
from app.schemas.data_rights import DataRightsRequestCreate, DataRightsRequestResponse
from app.services.data_rights import DataRightsService

router = APIRouter(prefix="/data-rights-requests", tags=["Data rights"])


def get_data_rights_service(
    db: DbSession = Depends(get_db), clock: Clock = Depends(get_clock)
) -> DataRightsService:
    return DataRightsService(db, clock)


@router.post(
    "",
    status_code=201,
    response_model=DataRightsRequestResponse,
    openapi_extra={"x-requirement": "FR-005"},
)
def create_data_rights_request(
    body: DataRightsRequestCreate,
    user: CurrentUser = Depends(get_current_user),
    service: DataRightsService = Depends(get_data_rights_service),
) -> DataRightsRequestResponse:
    return service.submit(user.account_id, body)


@router.get(
    "",
    response_model=Page[DataRightsRequestResponse],
    openapi_extra={"x-requirement": "FR-005"},
)
def list_data_rights_requests(
    page: PageParams = Depends(),
    user: CurrentUser = Depends(get_current_user),
    service: DataRightsService = Depends(get_data_rights_service),
) -> Page[DataRightsRequestResponse]:
    return service.list_for_owner(user.account_id, page.limit, page.offset)
