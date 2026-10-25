from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from app.models.user import Role


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: Role = Role.EMPLOYEE
    department: Optional[str] = None
    warehouse_id: Optional[int] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[Role] = None
    department: Optional[str] = None
    warehouse_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[Role] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str