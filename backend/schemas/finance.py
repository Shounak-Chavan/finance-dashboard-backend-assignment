from pydantic import BaseModel, ConfigDict, Field
from datetime import date as dt_date, datetime
from backend.models.finance import RecordType

# Base
class FinancialRecordBase(BaseModel):
    amount: float = Field(..., gt=0)
    type: RecordType
    category: str = Field(..., min_length=2, max_length=100)
    date: dt_date
    note: str | None = None

# Create
class FinancialRecordCreate(FinancialRecordBase):
    pass

# Update
class FinancialRecordUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    type: RecordType | None = None
    category: str | None = Field(default=None, min_length=2, max_length=100)
    date: dt_date | None = None
    note: str | None = None

# Response
class FinancialRecordResponse(FinancialRecordBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FinancialRecordListResponse(BaseModel):
    data: list[FinancialRecordResponse]
    page: int
    limit: int
    total: int