import asyncio

import pytest
import valkey.asyncio as valkey
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.auth.models import User
from src.auth.security import hash_password
from src.config import settings
from src.database import Base, get_db
from src.main import app

valkey_client = valkey.Redis.from_url(settings.VALKEY_URL)

engine = create_async_engine(settings.TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, autoflush=False
)


_DB_FIXTURES = {"db_session", "client", "verified_user", "unverified_user"}


@pytest.fixture(autouse=True)
async def setup_database(request: pytest.FixtureRequest):
    if not (_DB_FIXTURES & set(request.fixturenames)):
        yield
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def setup_cache(request: pytest.FixtureRequest):
    if not (_DB_FIXTURES & set(request.fixturenames)):
        yield ()
        return

    await valkey_client.flushdb()
    yield ()
    await valkey_client.flushdb()


@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def unverified_user(db_session: AsyncSession) -> User:
    hashed_pw = await asyncio.to_thread(hash_password, "SecurePassword123!")
    user = User(
        email="unverified@example.com",
        username="unverified",
        hashed_password=hashed_pw,
        is_verified=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def verified_user(db_session: AsyncSession) -> User:
    hashed_pw = await asyncio.to_thread(hash_password, "SecurePassword123!")
    user = User(
        email="verified@example.com",
        username="verified",
        hashed_password=hashed_pw,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
