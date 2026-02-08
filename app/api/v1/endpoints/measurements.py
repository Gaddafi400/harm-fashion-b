"""Measurement endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models.measurement import Measurement
from app.models.user import User
from app.schemas.measurement import MeasurementCreate, MeasurementUpdate, MeasurementResponse
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/measurements", tags=["Measurements"])

@router.post("/", response_model=MeasurementResponse, status_code=status.HTTP_201_CREATED)
async def create_measurement(
    measurement: MeasurementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "TAILOR"]))
):
    """Create a new measurement"""
    db_measurement = Measurement(**measurement.model_dump())
    db.add(db_measurement)
    await db.commit()
    await db.refresh(db_measurement)
    return db_measurement

@router.get("/customer/{customer_id}", response_model=List[MeasurementResponse])
async def get_customer_measurements(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all measurements for a customer"""
    result = await db.execute(
        select(Measurement).where(Measurement.customer_id == customer_id)
    )
    return result.scalars().all()

@router.put("/{measurement_id}", response_model=MeasurementResponse)
async def update_measurement(
    measurement_id: int,
    measurement_update: MeasurementUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN", "TAILOR"]))
):
    """Update a measurement"""
    result = await db.execute(select(Measurement).where(Measurement.id == measurement_id))
    measurement = result.scalar_one_or_none()
    
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurement not found"
        )
    
    update_data = measurement_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(measurement, field, value)
    
    await db.commit()
    await db.refresh(measurement)
    return measurement
