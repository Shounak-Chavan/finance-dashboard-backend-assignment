from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from backend.models.user import User
from backend.schemas.user import UserCreate
from backend.core.security import hash_password, verify_password
from backend.core.logging_config import get_logger

logger = get_logger(__name__)


async def create_user(
        db: AsyncSession,
        user_data: UserCreate
):
    existing_user = await get_user_by_email(db, user_data.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info("User created: id=%s email=%s role=%s", user.id, user.email, user.role.value)
    return user


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_users(
        db: AsyncSession
):
    result = await db.execute(select(User))
    return result.scalars().all()


async def update_user(
        db: AsyncSession,
        user_id: int,
        update_data: dict
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    for key, value in update_data.items():
        if value is not None:
            setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    logger.info("User updated: id=%s", user_id)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)

    if not user or not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user cannot log in",
        )

    logger.info("User authenticated: id=%s", user.id)
    return user