from pydantic import BaseModel, EmailStr
from datetime import datetime
from backend.models.user import UserRole
from pydantic import ConfigDict


# Base
class UserBase(BaseModel):
    name: str
    email: EmailStr


# Create 
class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.VIEWER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Update 
class UserUpdate(BaseModel):
    name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


# Response
class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"