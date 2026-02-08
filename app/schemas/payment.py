"""Payment schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class PaymentCreate(BaseModel):
    """Schema for creating a payment"""
    order_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)
    payment_date: date = Field(default_factory=date.today)
    payment_mode: str = Field(default="CASH", pattern="^(CASH|CARD|TRANSFER|MOBILE_MONEY|OTHER)$")
    reference: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

class PaymentResponse(BaseModel):
    """Payment response schema"""
    id: int
    order_id: int
    amount: Decimal
    payment_date: date
    payment_mode: str
    reference: Optional[str]
    notes: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
