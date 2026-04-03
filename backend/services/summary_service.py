from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.models.finance import FinancialRecord, RecordType

# SUMMARY
async def get_summary(db: AsyncSession):
    income_query = await db.execute(
        select(func.sum(FinancialRecord.amount)).where(
            FinancialRecord.type == RecordType.INCOME,
            FinancialRecord.is_deleted == False
        )
    )

    expense_query = await db.execute(
        select(func.sum(FinancialRecord.amount)).where(
            FinancialRecord.type == RecordType.EXPENSE,
            FinancialRecord.is_deleted == False
        )
    )

    income = income_query.scalar() or 0
    expense = expense_query.scalar() or 0

    return {
        "total_income": income,
        "total_expense": expense,
        "net_balance": income - expense
    }