from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db
from backend.services import user_service
from backend.schemas.user import UserCreate, UserUpdate
from backend.api.rbac import require_roles
from backend.models.user import UserRole  

router = APIRouter(prefix="/users", tags=["Users"])

# CREATE USER (ADMIN ONLY)
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.ADMIN]))]
)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    return await user_service.create_user(db, data)

# GET ALL USERS (ADMIN ONLY)
@router.get(
    "/",
    dependencies=[Depends(require_roles([UserRole.ADMIN]))]  
)
async def get_users(db: AsyncSession = Depends(get_db)):
    return await user_service.get_all_users(db)

# UPDATE USER (ADMIN ONLY)
@router.put(
    "/{user_id}",
    dependencies=[Depends(require_roles([UserRole.ADMIN]))]  
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await user_service.update_user(db, user_id, data)