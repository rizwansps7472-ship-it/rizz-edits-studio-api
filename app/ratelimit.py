"""Tiny in-memory sliding-window rate limiter (no extra dependencies).

Good enough for a studio site. For multi-worker production deployments, swap
for a Redis-backed limiter.
"""

import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, paths=("/api/inquiries",)):
        super().__init__(app)
        self.paths = paths
        self.hits: dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and request.url.path in self.paths:
            now = time.monotonic()
            window = 60.0
            limit = settings.RATE_LIMIT_PER_MINUTE
            ip = request.client.host if request.client else "unknown"
            q = self.hits[ip]
            while q and now - q[0] > window:
                q.popleft()
            if len(q) >= limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please wait a minute and try again."},
                )
            q.append(now)
        return await call_next(request)
