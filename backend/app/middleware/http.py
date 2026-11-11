"""Correlation id, request logging/metrics, error sanitising and security headers."""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import MutableMapping
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

from app.context import correlation_id_var, is_valid_correlation_id
from app.observability import metrics

logger = logging.getLogger("app.request")

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}


class RequestMiddleware:
    """Outermost middleware: correlation id, timing, logging, last-resort 500, headers."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope)
        inbound = request.headers.get("x-correlation-id")
        cid = inbound if inbound and is_valid_correlation_id(inbound) else uuid.uuid4().hex
        token = correlation_id_var.set(cid)
        start = time.perf_counter()
        status_holder = {"status": 500}

        async def send_wrapper(message: MutableMapping[str, Any]) -> None:
            if message["type"] == "http.response.start":
                status_holder["status"] = message["status"]
                headers = message.setdefault("headers", [])
                existing = {k.lower() for k, _ in headers}
                extra = {"X-Correlation-ID": cid, **SECURITY_HEADERS}
                if scope.get("path", "").startswith("/docs"):
                    extra.pop("Cache-Control")
                for k, v in extra.items():
                    if k.lower().encode() not in existing:
                        headers.append((k.lower().encode(), v.encode()))
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            logger.exception("Unhandled error")
            response: Response = JSONResponse(
                {"detail": "An unexpected error occurred"}, status_code=500
            )
            if status_holder["status"] == 500:
                await response(scope, receive, send_wrapper)
        finally:
            elapsed = time.perf_counter() - start
            route = str(getattr(scope.get("route"), "path", scope.get("path", "")))
            metrics.observe(scope["method"], route, status_holder["status"], elapsed)
            logger.info(
                "%s %s -> %s in %.1fms",
                scope["method"],
                route,
                status_holder["status"],
                elapsed * 1000,
            )
            correlation_id_var.reset(token)
