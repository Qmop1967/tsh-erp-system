from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role_id: int
    branch_id: int
    employee_code: Optional[str] = None
    phone: Optional[str] = None
    is_salesperson: Optional[bool] = False
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    employee_code: Optional[str] = None
    phone: Optional[str] = None
    is_salesperson: Optional[bool] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# Alias for compatibility
User = UserResponse


class UserLogin(BaseModel):
    email: EmailStr
    password: str 