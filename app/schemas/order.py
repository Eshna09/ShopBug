from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DiscountCreate(BaseModel):
    code: str
    discount_percent: float
    min_order_amount: float = 0.0
    max_discount_amount: Optional[float] = None


class DiscountResponse(BaseModel):
    id: int
    code: str
    discount_percent: float
    min_order_amount: float
    max_discount_amount: Optional[float]
    model_config = {"from_attributes": True}


class ApplyDiscountRequest(BaseModel):
    subtotal: float
    discount_id: int


class ApplyDiscountResponse(BaseModel):
    subtotal: float
    discount_amount: float
    post_discount_price: float


class OrderResponse(BaseModel):
    id: int
    user_id: int
    items_snapshot: str
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    created_at: datetime
    model_config = {"from_attributes": True}
