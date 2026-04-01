import os
import asyncio
import pytest

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# 🔥 Safe test environment (override BEFORE importing app)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ACCESS_TOKEN_SECRET_KEY"] = "test-secret"

from backend.db.base import Base
from backend.db.session import get_db
from backend.main import app

# 🔥 IMPORTANT: ensure models are registered
from backend.models import user, finance


@pytest.fixture()
def client():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSession = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async def override_get_db():
        async with TestingSession() as session:
            yield session

    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(init_models())

    # 🔥 override DB dependency
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

    asyncio.run(drop_models())
    asyncio.run(engine.dispose())