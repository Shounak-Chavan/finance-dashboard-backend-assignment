from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from backend.models.user import User, UserRole
from backend.schemas.user import UserCreate, UserUpdate
from backend.core.security import hash_password


# CREATE USER
async def create_user(db: AsyncSession, data: UserCreate):
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role or UserRole.VIEWER,
        is_active=True
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


# BOOTSTRAP ADMIN
async def bootstrap_admin(db: AsyncSession, data: UserCreate):
    result = await db.execute(select(User).where(User.role == UserRole.ADMIN))
    existing_admin = result.scalars().first()

    # If admin exists → update (idempotent behavior)
    if existing_admin:
        existing_admin.name = data.name
        existing_admin.hashed_password = hash_password(data.password)
        existing_admin.is_active = True

        await db.commit()
        await db.refresh(existing_admin)
        return existing_admin

    # If user exists with same email → upgrade to admin
    email_result = await db.execute(select(User).where(User.email == data.email))
    email_user = email_result.scalar_one_or_none()

    if email_user:
        email_user.name = data.name
        email_user.hashed_password = hash_password(data.password)
        email_user.role = UserRole.ADMIN
        email_user.is_active = True

        await db.commit()
        await db.refresh(email_user)
        return email_user

    # Create new admin
    admin_user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=UserRole.ADMIN,
        is_active=True,
    )

    db.add(admin_user)
    await db.commit()
    await db.refresh(admin_user)

    return admin_user


# GET ALL USERS
async def get_all_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()


# GET USER BY ID
async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# UPDATE USER
async def update_user(db: AsyncSession, user_id: int, data: UserUpdate):
    user = await get_user_by_id(db, user_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return user