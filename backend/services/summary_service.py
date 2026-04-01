from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case, func, select
from backend.models.finance import FinancialRecord, RecordType
from backend.models.user import UserRole


async def get_summary(
        db: AsyncSession,
        user_id: int,
        user_role: UserRole,
        target_user_id: int | None = None,
):
    filters = [FinancialRecord.is_deleted.is_(False)]
    if user_role == UserRole.ADMIN:
        if target_user_id is not None:
            filters.append(FinancialRecord.user_id == target_user_id)
    else:
        filters.append(FinancialRecord.user_id == user_id)

    income_result = await db.execute(
        select(func.sum(FinancialRecord.amount)).where(
            *filters,
            FinancialRecord.type == RecordType.INCOME,
        )
    )

    expense_result = await db.execute(
        select(func.sum(FinancialRecord.amount)).where(
            *filters,
            FinancialRecord.type == RecordType.EXPENSE,
        )
    )

    total_income = income_result.scalar() or 0
    total_expense = expense_result.scalar() or 0

    category_result = await db.execute(
        select(FinancialRecord.category, func.sum(FinancialRecord.amount))
        .where(*filters)
        .group_by(FinancialRecord.category)
        .order_by(func.sum(FinancialRecord.amount).desc())
    )

    recent_result = await db.execute(
        select(FinancialRecord)
        .where(*filters)
        .order_by(FinancialRecord.date.desc(), FinancialRecord.id.desc())
        .limit(5)
    )

    trend_result = await db.execute(
        select(
            func.extract("year", FinancialRecord.date).label("year"),
            func.extract("month", FinancialRecord.date).label("month"),
            func.sum(
                case(
                    (FinancialRecord.type == RecordType.INCOME, FinancialRecord.amount),
                    else_=0,
                )
            ).label("income"),
            func.sum(
                case(
                    (FinancialRecord.type == RecordType.EXPENSE, FinancialRecord.amount),
                    else_=0,
                )
            ).label("expense"),
        )
        .where(*filters)
        .group_by(
            func.extract("year", FinancialRecord.date),
            func.extract("month", FinancialRecord.date),
        )
        .order_by(
            func.extract("year", FinancialRecord.date),
            func.extract("month", FinancialRecord.date),
        )
    )

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": total_income - total_expense,
        "category_totals": [
            {"category": row[0], "total": row[1]} for row in category_result.all()
        ],
        "recent_activity": [
            {
                "id": row.id,
                "amount": row.amount,
                "type": row.type.value,
                "category": row.category,
                "date": row.date.isoformat(),
                "note": row.note,
                "user_id": row.user_id,
            }
            for row in recent_result.scalars().all()
        ],
        "monthly_trends": [
            {
                "year": int(row.year),
                "month": int(row.month),
                "income": row.income or 0,
                "expense": row.expense or 0,
                "net": (row.income or 0) - (row.expense or 0),
            }
            for row in trend_result.all()
        ],
    }