from contextlib import asynccontextmanager

from fastapi import FastAPI

import src.auth.models  # noqa: F401
from src.ai.router import ai_router
from src.auth.router import auth_router
from src.database import engine
from src.exceptions import AppException, app_exception_handler
from src.observability import setup_observability


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
setup_observability(app)

app.include_router(auth_router)
app.include_router(ai_router)

app.add_exception_handler(AppException, app_exception_handler)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
