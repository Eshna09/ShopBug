import json
import os
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.order import Order, Discount
from app.services import cart_service, discount_service

TAX_RATE = float(os.getenv("TAX_RATE", "0.10"))


def checkout(db: Session, user_id: int, discount_id: int | None = None) -> Order:
    items = cart_service.get_cart_items(db, user_id)
    if not items:
        raise HTTPException(status_code=400, detail="Cannot checkout with an empty cart.")
    for item in items:
        if item.product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{item.product.name}'.",
            )
    subtotal = cart_service.get_cart_subtotal(db, user_id)
    discount_amount = 0.0
    if discount_id is not None:
        discount = db.query(Discount).filter(Discount.id == discount_id).first()
        if not discount:
            raise HTTPException(status_code=404, detail="Discount not found.")
        discount_amount = discount_service.calculate_discount_amount(subtotal, discount)
    post_discount = subtotal - discount_amount
    tax_amount = post_discount * TAX_RATE
    total_amount = post_discount + tax_amount
    snapshot = json.dumps([
        {
            "product_id": i.product_id,
            "name": i.product.name,
            "price": i.product.price,
            "quantity": i.quantity,
        }
        for i in items
    ])
    order = Order(
        user_id=user_id,
        items_snapshot=snapshot,
        subtotal=subtotal,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        total_amount=total_amount,
    )
    db.add(order)
    for item in items:
        item.product.stock -= item.quantity
        item.product.available = item.product.stock > 0
    db.commit()
    db.refresh(order)
    return order
