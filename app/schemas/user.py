"""User schemas"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = Field(..., pattern="^(ADMIN|TAILOR|CASHIER)$")

class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(ADMIN|TAILOR|CASHIER)$")
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str
