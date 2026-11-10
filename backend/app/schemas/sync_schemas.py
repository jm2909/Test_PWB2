import uuid

from pydantic import BaseModel

from app.schemas.device_schemas import SyncSummary

__all__ = ["SyncRequest", "SyncSummary"]


class SyncRequest(BaseModel):
    device_connection_id: uuid.UUID
