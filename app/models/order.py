"""Order model"""

from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Text, Enum, DateTime, func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    """Order status enumeration"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    COLLECTED = "COLLECTED"
    CANCELLED = "CANCELLED"


class Order(Base):
    """Order model representing a customer's tailoring order"""
    
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    total_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    amount_paid = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    due_date = Column(Date, nullable=False, index=True)
    collection_date = Column(Date, nullable=True)
    
    status = Column(
        Enum(OrderStatus, native_enum=False),
        nullable=False,
        default=OrderStatus.PENDING,
        index=True
    )
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    measurements = relationship("Measurement", back_populates="order")
    creator = relationship("User", foreign_keys=[created_by])
    assigned_tailor = relationship("User", foreign_keys=[assigned_to])

    def __repr__(self):
        return f"<Order {self.order_number} - Customer: {self.customer_id} - Status: {self.status}>"
    
    def __repr__(self):
        return f"<Order {self.order_number} - Customer: {self.customer_id} - Status: {self.status}>"
    
    @property
    def balance(self):
        """Calculate balance"""
        return float(self.total_amount) - float(self.amount_paid)
    
    @property
    def is_fully_paid(self):
        """Check if order is fully paid"""
        return self.balance <= 0
    
    @property
    def is_overdue(self):
        """Check if order is overdue"""
        from datetime import date
        return self.due_date < date.today() and self.status not in [OrderStatus.COLLECTED, OrderStatus.CANCELLED]
