from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.user import User, UserRole
from backend.core.security import hash_password
from backend.core.config import settings


async def seed_admin(db: AsyncSession):
    # check if admin already exists
    result = await db.execute(
        select(User).where(User.role == UserRole.ADMIN)
    )
    admin = result.scalars().first()

    if admin:
        return  # already exists

    # use env-based config
    admin_user = User(
        name=settings.ADMIN_NAME,
        email=settings.ADMIN_EMAIL,
        hashed_password=hash_password(settings.ADMIN_PASSWORD),
        role=UserRole.ADMIN,
        is_active=True
    )

    db.add(admin_user)
    await db.commit()