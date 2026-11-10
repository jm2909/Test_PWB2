from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.common_schemas import ErrorResponse
from app.schemas.device_schemas import DeviceConnectionResponse
from app.schemas.sync_schemas import SyncRequest
from app.services.consent_service import ProcessingBlockedError
from app.services.device_service import to_response
from app.services.sync_service import ConnectionNotFoundError, SyncIngestionService, SyncUnsupportedError

router = APIRouter(tags=["sync"])


@router.post(
    "/sync",
    response_model=DeviceConnectionResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def run_sync(
    payload: SyncRequest,
    request: Request,
    idempotency_key: str = Header(min_length=16, max_length=128, alias="Idempotency-Key"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeviceConnectionResponse:
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    try:
        row, summary = SyncIngestionService(db).sync(
            user.id, payload.device_connection_id, idempotency_key, correlation_id
        )
    except ConnectionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Device connection not found.") from exc
    except ProcessingBlockedError as exc:
        raise HTTPException(status_code=403, detail=exc.explanation) from exc
    except SyncUnsupportedError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    db.refresh(row)
    return to_response(row, summary)
