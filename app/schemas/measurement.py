"""Measurement schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class MeasurementCreate(BaseModel):
    """Schema for creating a measurement"""
    customer_id: int = Field(..., gt=0)
    order_id: Optional[int] = Field(None, gt=0)
    measurement_type: str = Field(..., pattern="^(MALE|FEMALE|GENERAL)$")
    data: Dict[str, Any]
    notes: Optional[str] = None

class MeasurementUpdate(BaseModel):
    """Schema for updating a measurement"""
    data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class MeasurementResponse(BaseModel):
    """Measurement response schema"""
    id: int
    customer_id: int
    order_id: Optional[int]
    measurement_type: str
    data: Dict[str, Any]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
