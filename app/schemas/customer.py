"""Customer schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class CustomerBase(BaseModel):
    """Base customer schema"""
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    gender: Optional[str] = Field(None, pattern="^(MALE|FEMALE|OTHER)$")
    email: Optional[str] = None
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    """Schema for creating a customer"""
    pass

class CustomerUpdate(BaseModel):
    """Schema for updating a customer"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    gender: Optional[str] = Field(None, pattern="^(MALE|FEMALE|OTHER)$")
    email: Optional[str] = None
    address: Optional[str] = None

class CustomerResponse(CustomerBase):
    """Customer response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PaginatedResponse(BaseModel):
    customers: List[CustomerResponse]
    total: int
    skip: int
    limit: int
    has_more: bool