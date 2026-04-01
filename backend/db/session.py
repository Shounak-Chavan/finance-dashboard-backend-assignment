from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings
from backend.db.base import Base

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


async def init_db() -> None:
    # Import models here to populate SQLAlchemy metadata before create_all.
    from backend.models import finance, user  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)