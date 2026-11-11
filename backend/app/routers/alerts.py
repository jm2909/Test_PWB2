from __future__ import annotations

import uuid
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DbSession

from app.clock import Clock
from app.database import get_db
from app.deps import CurrentUser, get_clock, get_current_user
from app.schemas.alert import AlertResponse
from app.schemas.common import Page, PageParams
from app.services.alert import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts and goals"])


def get_alert_service(
    db: DbSession = Depends(get_db), clock: Clock = Depends(get_clock)
) -> AlertService:
    return AlertService(db, clock)


@router.get("", response_model=Page[AlertResponse], openapi_extra={"x-requirement": "FR-016"})
def list_alerts(
    state: Literal["active", "acknowledged"] | None = Query(None),
    page: PageParams = Depends(),
    user: CurrentUser = Depends(get_current_user),
    service: AlertService = Depends(get_alert_service),
) -> Page[AlertResponse]:
    return service.list_alerts(user.account_id, state, page.limit, page.offset)


@router.post(
    "/{alert_id}/acknowledgements",
    response_model=AlertResponse,
    openapi_extra={"x-requirement": "FR-016"},
)
def acknowledge_alert(
    alert_id: uuid.UUID,
    user: CurrentUser = Depends(get_current_user),
    service: AlertService = Depends(get_alert_service),
) -> AlertResponse:
    return service.acknowledge(user.account_id, alert_id)
