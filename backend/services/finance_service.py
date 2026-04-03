from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, date as dt_date
from sqlalchemy import select, or_
from fastapi import HTTPException, status

from backend.models.finance import FinancialRecord, RecordType
from backend.schemas.finance import FinancialRecordCreate, FinancialRecordUpdate


# CREATE
async def create_record(db: AsyncSession, data: FinancialRecordCreate, user_id: int):
    record = FinancialRecord(**data.model_dump(), user_id=user_id)

    db.add(record)
    await db.commit()
    await db.refresh(record)

    return record


# GET (WITH FILTERS + PAGINATION)
async def get_records(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    category: str | None = None,
    record_type: RecordType | None = None,
    start_date: dt_date | None = None,
    end_date: dt_date | None = None,
    user_id: int | None = None,
):
    query = select(FinancialRecord).where(FinancialRecord.is_deleted == False)

    if category:
        query = query.where(FinancialRecord.category == category)

    if record_type:
        query = query.where(FinancialRecord.type == record_type)

    if start_date:
        query = query.where(FinancialRecord.date >= start_date)

    if end_date:
        query = query.where(FinancialRecord.date <= end_date)

    if user_id:
        query = query.where(FinancialRecord.user_id == user_id)

    result = await db.execute(
        query.order_by(FinancialRecord.date.desc(), FinancialRecord.id.desc())
        .offset(skip)
        .limit(limit)
    )

    records = result.scalars().all()

    return records


# SEARCH (CATEGORY)
async def search_records(
    db: AsyncSession,
    q: str,
    skip: int = 0,
    limit: int = 10,
    user_id: int | None = None,
):
    query = select(FinancialRecord).where(
        FinancialRecord.is_deleted == False,
        or_(
            FinancialRecord.category.ilike(f"%{q}%"),
            FinancialRecord.note.ilike(f"%{q}%"),
        ),
    )

    if user_id:
        query = query.where(FinancialRecord.user_id == user_id)

    result = await db.execute(
        query.order_by(FinancialRecord.date.desc(), FinancialRecord.id.desc())
        .offset(skip)
        .limit(limit)
    )

    return result.scalars().all()


#GET BY ID (OPTIONAL USER CHECK)
async def get_record_by_id(
    db: AsyncSession,
    record_id: int,
    user_id: int | None = None,
):
    query = select(FinancialRecord).where(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False,
    )

    if user_id:
        query = query.where(FinancialRecord.user_id == user_id)

    result = await db.execute(query)
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )

    return record


#UPDATE
async def update_record(
    db: AsyncSession,
    record_id: int,
    data: FinancialRecordUpdate,
    user_id: int | None = None,
):
    record = await get_record_by_id(db, record_id, user_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)

    await db.commit()
    await db.refresh(record)

    return record


# DELETE (SOFT DELETE)
async def delete_record(
    db: AsyncSession,
    record_id: int,
    user_id: int | None = None,
):
    record = await get_record_by_id(db, record_id, user_id)

    record.is_deleted = True
    record.deleted_at = datetime.now(timezone.utc)

    await db.commit()

    return {"message": "Record deleted successfully"}