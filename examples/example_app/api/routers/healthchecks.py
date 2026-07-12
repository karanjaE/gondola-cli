import logging

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health/db")
async def health_check_db(session: AsyncSession = Depends(get_db)):
    """Check if the database is healthy.

    Args:
        session (AsyncSession): The database session.

    Returns:
        JSONResponse: A response indicating whether the database is healthy.
    """
    db_status = "healthy"
    try:
        await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("Database health check failed: %s", e)
        db_status = "unhealthy"

    is_healthy = db_status == "healthy"
    return JSONResponse(
        status_code=status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "healthy" if is_healthy else "unhealthy",
            "database": db_status,
        },
    )

@router.get("/health")
def health_check():
    """Health check endpoint.

    Returns:
        JSONResponse: A response indicating the health of the application.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
        },
    )
