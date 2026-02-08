"""Order schemas"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.order import OrderStatus


class OrderBase(BaseModel):
    """Base order schema"""
    customer_id: int
    total_amount: Decimal = Field(ge=0)
    due_date: date
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Order creation schema"""
    pass


class OrderUpdate(BaseModel):
    """Order update schema"""
    total_amount: Optional[Decimal] = Field(None, ge=0)
    due_date: Optional[date] = None
    collection_date: Optional[date] = None
    status: Optional[OrderStatus] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None


class OrderAssign(BaseModel):
    """Order assignment schema"""
    assigned_to: Optional[int] = None


class TailorInfo(BaseModel):
    """Tailor information"""
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class CustomerInfo(BaseModel):
    """Customer information for order response"""
    id: int
    name: str
    phone: str

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(OrderBase):
    """Order response schema"""
    id: int
    order_number: str
    amount_paid: Decimal
    collection_date: Optional[date] = None
    status: OrderStatus
    created_by: Optional[int] = None
    assigned_to: Optional[int] = None
    assigned_tailor: Optional[TailorInfo] = None
    customer: Optional[CustomerInfo] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# """Order schemas"""
# from datetime import date, datetime
# from decimal import Decimal
# from typing import Optional
#
# from pydantic import BaseModel, Field, ConfigDict, field_validator
#
#
# class OrderCreate(BaseModel):
#     """Schema for creating an order"""
#     customer_id: int = Field(..., gt=0)
#     total_amount: Decimal = Field(..., ge=0)
#     due_date: date
#     notes: Optional[str] = Field(None, max_length=1000)
#
#
# class OrderUpdate(BaseModel):
#     """Schema for updating an order"""
#     total_amount: Optional[Decimal] = Field(None, ge=0)
#     due_date: Optional[date] = None
#     collection_date: Optional[date] = None
#     status: Optional[str] = Field(None, pattern="^(PENDING|IN_PROGRESS|READY|COLLECTED|CANCELLED)$")
#     notes: Optional[str] = Field(None, max_length=1000)
#
#     @field_validator("collection_date", mode="before")
#     @classmethod
#     def empty_string_to_none(cls, v):
#         if v == "":
#             return None
#         return v
#
#
#
# class OrderResponse(BaseModel):
#     """Order response schema"""
#     id: int
#     order_number: str
#     customer_id: int
#     total_amount: Decimal
#     amount_paid: Decimal
#     due_date: date
#     collection_date: Optional[date] = None
#     status: str
#     notes: Optional[str]
#     created_at: datetime
#     updated_at: datetime
#     model_config = ConfigDict(from_attributes=True)
