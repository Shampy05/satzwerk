from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

import src.auth.models  # noqa: F401
from src.ai.router import ai_router
from src.auth.router import auth_router
from src.database import Base, engine
from src.exceptions import AppException, app_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS "
                "target_language VARCHAR(5) NOT NULL DEFAULT 'de'"
            )
        )
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(ai_router)

app.add_exception_handler(AppException, app_exception_handler)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
