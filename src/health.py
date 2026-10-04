from fastapi import APIRouter, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.dependencies import DbDep
from src.exceptions import DatabaseUnavailableException

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/live", status_code=status.HTTP_200_OK)
async def liveness():
    return {"status": "alive"}


@health_router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness(db: DbDep):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except SQLAlchemyError:
        raise DatabaseUnavailableException()
