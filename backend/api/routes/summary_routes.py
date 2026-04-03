from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db
from backend.services import summary_service
from backend.api.rbac import require_roles
from backend.models.user import UserRole  

router = APIRouter(prefix="/summary", tags=["Summary"])

# GET SUMMARY
@router.get("/")
async def get_summary(
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles([UserRole.ADMIN, UserRole.ANALYST, UserRole.VIEWER]))  
):
    return await summary_service.get_summary(db)