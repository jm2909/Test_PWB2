"""Domain exceptions mapped to the common {"detail": ...} error form."""

from __future__ import annotations


class DomainError(Exception):
    status_code = 400
    default_detail = "Request could not be processed"

    def __init__(self, detail: str | None = None, headers: dict[str, str] | None = None) -> None:
        self.detail = detail or self.default_detail
        self.headers = headers
        super().__init__(self.detail)


class AuthenticationError(DomainError):
    status_code = 401
    default_detail = "Invalid credentials"


class PermissionDeniedError(DomainError):
    status_code = 403
    default_detail = "Access denied"


class NotFoundError(DomainError):
    status_code = 404
    default_detail = "Resource not found"


class ConflictError(DomainError):
    status_code = 409
    default_detail = "Conflict"


class RateLimitedError(DomainError):
    status_code = 429
    default_detail = "Too many attempts. Try again later."
