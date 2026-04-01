import enum
from sqlalchemy import Boolean, Column, Integer, String, Float, Date, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.db.base import Base


class RecordType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    amount = Column(Float, nullable=False)
    type = Column(Enum(RecordType), nullable=False)
    category = Column(String(100), nullable=False, index=True)

    date = Column(Date, nullable=False, index=True)
    note = Column(String(255), nullable=True)

    # Soft-delete fields keep historical data while hiding deleted records.
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="records")