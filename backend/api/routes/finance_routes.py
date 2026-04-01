from fastapi import APIRouter, Depends, Query
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import get_db
from backend.schemas.finance import (
    FinancialRecordCreate,
    FinancialRecordListResponse,
    FinancialRecordResponse,
    FinancialRecordUpdate,
)
from backend.services import finance_service
from backend.api.rbac import require_roles
from backend.models.finance import RecordType
from backend.models.user import UserRole

router = APIRouter(prefix="/records", tags=["Finance"])


@router.post("/", response_model=FinancialRecordResponse)
async def create_record(
    data: FinancialRecordCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles([UserRole.ADMIN])),
):
    return await finance_service.create_record(db, user.id, data)


@router.get("/", response_model=FinancialRecordListResponse)
async def get_records(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    category: str | None = Query(default=None),
    record_type: RecordType | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    user_id: int | None = Query(default=None, ge=1),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles([UserRole.ADMIN, UserRole.ANALYST])),
):
    return await finance_service.get_records(
        db,
        user.id,
        user.role,
        page,
        limit,
        category,
        record_type,
        start_date,
        end_date,
        user_id,
    )


@router.get("/search", response_model=FinancialRecordListResponse)
async def search_records(
    q: str = Query(..., min_length=1, max_length=100),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    user_id: int | None = Query(default=None, ge=1),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles([UserRole.ADMIN, UserRole.ANALYST])),
):
    return await finance_service.search_records(
        db,
        user.id,
        user.role,
        q,
        page,
        limit,
        user_id,
    )


@router.patch("/{record_id}", response_model=FinancialRecordResponse)
async def update_record(
    record_id: int,
    payload: FinancialRecordUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles([UserRole.ADMIN])),
):
    return await finance_service.update_record(db, record_id, user.id, user.role, payload)


@router.delete("/{record_id}")
async def delete_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_roles([UserRole.ADMIN])),
):
    return await finance_service.delete_record(db, record_id, user.id, user.role)