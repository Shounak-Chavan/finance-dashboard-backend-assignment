from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import get_db
from backend.schemas.user import UserCreate, UserResponse, UserUpdate
from backend.services import user_service
from backend.api.rbac import require_roles
from backend.models.user import User, UserRole

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/bootstrap-admin", response_model=UserResponse)
async def bootstrap_admin(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    total_users_result = await db.execute(select(func.count()).select_from(User))
    total_users = total_users_result.scalar() or 0

    if total_users > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bootstrap admin is only allowed when no users exist",
        )

    user.role = UserRole.ADMIN
    return await user_service.create_user(db, user)


@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles([UserRole.ADMIN]))
):
    return await user_service.create_user(db, user)


@router.get("/", response_model=list[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles([UserRole.ADMIN]))
):
    return await user_service.get_users(db)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles([UserRole.ADMIN])),
):
    return await user_service.update_user(db, user_id, payload.model_dump(exclude_unset=True))