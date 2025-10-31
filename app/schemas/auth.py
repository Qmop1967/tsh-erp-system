from pydantic import BaseModel
from typing import Optional, List

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None  # For mobile apps - 30 days expiration
    user: dict

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    branch: str
    permissions: List[str] = []

class TokenData(BaseModel):
    email: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
