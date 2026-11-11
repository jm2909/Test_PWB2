from __future__ import annotations

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    limit: int
    offset: int
    total: int


class PageParams:
    def __init__(
        self,
        limit: int = Query(25, ge=1, le=100),
        offset: int = Query(0, ge=0),
    ) -> None:
        self.limit = limit
        self.offset = offset
