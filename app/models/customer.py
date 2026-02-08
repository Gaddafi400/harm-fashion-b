"""Customer model"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class Gender(str, enum.Enum):
    """Gender enumeration"""
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class Customer(Base):
    """Customer model representing tailoring customers"""
    
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    gender = Column(Enum(Gender, native_enum=False), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    measurements = relationship("Measurement", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer {self.name} - {self.phone}>"
