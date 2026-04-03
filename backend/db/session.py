from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings
from backend.db.seed import seed_admin  # ✅ import seed

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


# ONLY SEED HERE 
async def init_db() -> None:
    async with AsyncSessionLocal() as db:
        await seed_admin(db)


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db