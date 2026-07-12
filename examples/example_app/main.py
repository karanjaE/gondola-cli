"""
Example FastAPI application entrypoint.

Wires up logging, async PostgreSQL (SQLModel + asyncpg), CORS,
API-Version header handling (defaults to v1), and router mounting.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from api.routers import api_router
from core.config import get_settings
from core.database import close_db, init_db
from core.logging import setup_logging

settings = get_settings()
logger = logging.getLogger(__name__)


class APIVersionMiddleware(BaseHTTPMiddleware):
    """Read API-Version header; default to configured version if omitted."""

    async def dispatch(self, request: Request, call_next):
        raw = request.headers.get("API-Version")
        if raw is None or not raw.strip():
            request.state.api_version = settings.api_default_version
        else:
            request.state.api_version = raw.strip()
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    setup_logging()
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)

    await init_db()
    logger.info("Database pool initialised")

    yield

    await close_db()
    logger.info("Database pool disposed")


app = FastAPI(
    title=settings.app_name,
    description="Example HTTP API",
    version=settings.app_version,
    lifespan=lifespan,
    debug=settings.debug,
)

app.add_middleware(APIVersionMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "ok", "status": "success", "version": settings.app_version}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
