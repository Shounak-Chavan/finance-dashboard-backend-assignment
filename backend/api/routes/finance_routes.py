from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db
from backend.services import finance_service
from backend.schemas.finance import FinancialRecordCreate, FinancialRecordUpdate
from backend.api.rbac import require_roles
from backend.models.user import UserRole  

router = APIRouter(prefix="/records", tags=["Finance"])

# CREATE RECORD
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_record(
    data: FinancialRecordCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles([UserRole.ADMIN]))  
):
    return await finance_service.create_record(db, data, user.id)

# GET RECORDS (WITH FILTERS + PAGINATION)
@router.get("/")
async def get_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles([UserRole.ADMIN, UserRole.ANALYST, UserRole.VIEWER]))  
):
    return await finance_service.get_records(db, skip, limit)

# UPDATE RECORD
@router.put("/{record_id}")
async def update_record(
    record_id: int,
    data: FinancialRecordUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles([UserRole.ADMIN]))  
):
    return await finance_service.update_record(db, record_id, data)

# DELETE RECORD (SOFT DELETE)
@router.delete("/{record_id}")
async def delete_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles([UserRole.ADMIN]))  
):
    return await finance_service.delete_record(db, record_id)