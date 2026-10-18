"""Rizz Edits Studio API — FastAPI backend for the studio website.

Run locally:
    uvicorn app.main:app --reload --port 8000
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .ratelimit import RateLimitMiddleware
from .routers import inquiries

logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.APP_NAME, docs_url="/api/docs", redoc_url=None)

# CORS: only the configured site origins may call the API from a browser.
# ALLOWED_ORIGINS="*" is allowed for local development only.
if settings.ALLOWED_ORIGINS:
    allow_origins = ["*"] if settings.ALLOWED_ORIGINS == ["*"] else settings.ALLOWED_ORIGINS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-API-Key"],
        max_age=600,
    )

app.add_middleware(RateLimitMiddleware)
app.include_router(inquiries.router)


@app.on_event("startup")
def _create_tables():
    Base.metadata.create_all(bind=engine)
