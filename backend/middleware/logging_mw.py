"""Middleware для логування HTTP-запитів."""

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.logging_config import request_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Логує кожен вхідний запит із часом обробки."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        request_logger.info(
            "→ %s %s [%s]",
            request.method,
            request.url.path,
            request_id,
        )

        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        request_logger.info(
            "← %s %s %d %.1fms [%s]",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            request_id,
        )
        return response
