from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from app.database import Base


class Discount(Base):
    __tablename__ = "discounts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False, index=True)
    discount_percent = Column(Float, nullable=False)
    min_order_amount = Column(Float, nullable=False, default=0.0)
    max_discount_amount = Column(Float, nullable=True)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    items_snapshot = Column(Text, nullable=False)
    subtotal = Column(Float, nullable=False)
    discount_amount = Column(Float, nullable=False, default=0.0)
    tax_amount = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
