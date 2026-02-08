"""Measurement model"""

import enum

from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class MeasurementType(str, enum.Enum):
    """Measurement type enumeration"""
    MALE = "MALE"
    FEMALE = "FEMALE"
    GENERAL = "GENERAL"


class Measurement(Base):
    """Measurement model representing customer measurements"""

    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    measurement_type = Column(
        Enum(MeasurementType, native_enum=False),
        nullable=False,
        default=MeasurementType.GENERAL
    )
    data = Column(JSONB, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="measurements")
    order = relationship("Order", back_populates="measurements")

    def __repr__(self):
        return f"<Measurement {self.id} - Customer: {self.customer_id} - Type: {self.measurement_type}>"
