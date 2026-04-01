from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, func
from fastapi import HTTPException, status
from datetime import date, datetime, timezone

from backend.models.finance import FinancialRecord, RecordType
from backend.models.user import UserRole
from backend.schemas.finance import FinancialRecordCreate, FinancialRecordUpdate
from backend.core.logging_config import get_logger

logger = get_logger(__name__)


def _base_filters(user_id: int, user_role: UserRole, target_user_id: int | None = None):
    filters = [FinancialRecord.is_deleted.is_(False)]
    if user_role == UserRole.ADMIN:
        if target_user_id is not None:
            filters.append(FinancialRecord.user_id == target_user_id)
    else:
        filters.append(FinancialRecord.user_id == user_id)
    return filters


async def create_record(
        db: AsyncSession,
        user_id: int,
        data: FinancialRecordCreate
):
    record = FinancialRecord(
        user_id=user_id,
        amount=data.amount,
        type=data.type,
        category=data.category,
        date=data.date,
        note=data.note
    )

    db.add(record)
    await db.commit()
    await db.refresh(record)
    logger.info("Record created: id=%s user_id=%s", record.id, user_id)
    return record


async def get_records(
        db: AsyncSession,
        user_id: int,
        user_role: UserRole,
        page: int = 1,
        limit: int = 10,
        category: str | None = None,
        record_type: RecordType | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        target_user_id: int | None = None,
):
    offset = (page - 1) * limit

    filters = _base_filters(user_id, user_role, target_user_id)

    if category:
        filters.append(FinancialRecord.category == category)
    if record_type:
        filters.append(FinancialRecord.type == record_type)
    if start_date:
        filters.append(FinancialRecord.date >= start_date)
    if end_date:
        filters.append(FinancialRecord.date <= end_date)

    result = await db.execute(
        select(FinancialRecord)
        .where(*filters)
        .order_by(FinancialRecord.date.desc(), FinancialRecord.id.desc())
        .offset(offset)
        .limit(limit)
    )
    records = result.scalars().all()

    total_result = await db.execute(
        select(func.count()).select_from(FinancialRecord).where(*filters)
    )
    total = total_result.scalar()

    return {
        "data": records,
        "page": page,
        "limit": limit,
        "total": total
    }


async def search_records(
    db: AsyncSession,
    user_id: int,
    user_role: UserRole,
    query: str,
    page: int = 1,
    limit: int = 10,
    target_user_id: int | None = None,
):
    offset = (page - 1) * limit
    filters = _base_filters(user_id, user_role, target_user_id)

    text_filter = or_(
        FinancialRecord.category.ilike(f"%{query}%"),
        FinancialRecord.note.ilike(f"%{query}%"),
    )

    result = await db.execute(
        select(FinancialRecord)
        .where(*filters, text_filter)
        .order_by(FinancialRecord.date.desc(), FinancialRecord.id.desc())
        .offset(offset)
        .limit(limit)
    )
    records = result.scalars().all()

    total_result = await db.execute(
        select(func.count())
        .select_from(FinancialRecord)
        .where(*filters, text_filter)
    )
    total = total_result.scalar() or 0

    return {
        "data": records,
        "page": page,
        "limit": limit,
        "total": total,
    }


async def delete_record(
        db: AsyncSession,
        record_id: int,
        user_id: int,
        user_role: UserRole,
):
    filters = _base_filters(user_id, user_role)
    filters.append(FinancialRecord.id == record_id)

    result = await db.execute(select(FinancialRecord).where(*filters))

    record = result.scalars().first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found"
        )

    record.is_deleted = True
    record.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    logger.info("Record soft-deleted: id=%s by user_id=%s", record_id, user_id)
    return {"message": "Record deleted successfully"}


async def update_record(
    db: AsyncSession,
    record_id: int,
    user_id: int,
    user_role: UserRole,
    payload: FinancialRecordUpdate,
):
    filters = _base_filters(user_id, user_role)
    filters.append(FinancialRecord.id == record_id)

    result = await db.execute(select(FinancialRecord).where(*filters))
    record = result.scalars().first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    await db.commit()
    await db.refresh(record)
    logger.info("Record updated: id=%s by user_id=%s", record_id, user_id)
    return record