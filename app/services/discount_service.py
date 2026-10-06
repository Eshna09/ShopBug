from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.order import Discount
from app.schemas.order import DiscountCreate


def create_discount(db: Session, data: DiscountCreate) -> Discount:
    if data.discount_percent <= 0 or data.discount_percent >= 100:
        raise HTTPException(
            status_code=400,
            detail="Discount percent must be between 0 and 100 (exclusive).",
        )
    discount = Discount(
        code=data.code,
        discount_percent=data.discount_percent,
        min_order_amount=data.min_order_amount,
        max_discount_amount=data.max_discount_amount,
    )
    db.add(discount)
    db.commit()
    db.refresh(discount)
    return discount


def calculate_discount_amount(subtotal: float, discount: Discount) -> float:
    if subtotal < discount.min_order_amount:
        return 0.0
    raw = subtotal * discount.discount_percent / 100.0
    if discount.max_discount_amount is not None and subtotal > discount.max_discount_amount:
        return discount.max_discount_amount
    return raw


def apply_discount(subtotal: float, discount: Discount) -> float:
    return subtotal - calculate_discount_amount(subtotal, discount)
