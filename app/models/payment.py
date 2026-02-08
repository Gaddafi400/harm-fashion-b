"""Payment model"""

from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey, String, Text, DateTime, Enum, func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class PaymentMode(str, enum.Enum):
    """Payment mode enumeration"""
    CASH = "CASH"
    CARD = "CARD"
    TRANSFER = "TRANSFER"
    MOBILE_MONEY = "MOBILE_MONEY"
    OTHER = "OTHER"


class Payment(Base):
    """Payment model representing payments made for orders"""
    
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date, nullable=False, index=True)
    payment_mode = Column(
        Enum(PaymentMode, native_enum=False),
        nullable=False,
        default=PaymentMode.CASH
    )
    reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="payments")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<Payment {self.id} - Order: {self.order_id} - Amount: {self.amount}>"
