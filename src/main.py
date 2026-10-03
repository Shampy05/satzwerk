from contextlib import asynccontextmanager

from fastapi import FastAPI

import src.auth.models  # noqa: F401
from src.auth.router import auth_router
from src.database import Base, engine
from src.exceptions import AppException, app_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)

app.add_exception_handler(AppException, app_exception_handler)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
