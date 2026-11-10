from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.common_schemas import ErrorResponse
from app.schemas.device_schemas import (
    DeviceConnectionCreate,
    DeviceConnectionListResponse,
    DeviceConnectionResponse,
)
from app.services.consent_service import ProcessingBlockedError
from app.services.device_service import DeviceService, UnsupportedConnectionError, to_response

router = APIRouter(tags=["device-connections"])


@router.get(
    "/device-connections",
    response_model=DeviceConnectionListResponse,
    responses={401: {"model": ErrorResponse}},
)
def list_device_connections(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeviceConnectionListResponse:
    items = [to_response(r) for r in DeviceService(db).list_for_user(user.id)]
    return DeviceConnectionListResponse(items=items, total=len(items))


@router.post(
    "/device-connections",
    response_model=DeviceConnectionResponse,
    status_code=201,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def create_device_connection(
    payload: DeviceConnectionCreate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeviceConnectionResponse:
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    try:
        row = DeviceService(db).connect(user.id, payload, correlation_id)
    except UnsupportedConnectionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ProcessingBlockedError as exc:
        raise HTTPException(status_code=403, detail=exc.explanation) from exc
    return to_response(row)
