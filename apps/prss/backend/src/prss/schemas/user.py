"""User schemas"""
from pydantic import BaseModel, EmailStr
from prss.models.base import UserRole


class UserCreate(BaseModel):
    """Create user"""
    username: str
    email: EmailStr
    full_name: str
    role: UserRole
    password: str


class Token(BaseModel):
    """JWT Token"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    username: str
    role: UserRole
    scopes: list[str] = []
