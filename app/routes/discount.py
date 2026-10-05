from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.order import (
    DiscountCreate,
    DiscountResponse,
    ApplyDiscountRequest,
    ApplyDiscountResponse,
)
from app.services import discount_service
from app.models.order import Discount

router = APIRouter()


@router.post("/create", response_model=DiscountResponse, status_code=201)
def create_discount(data: DiscountCreate, db: Session = Depends(get_db)):
    return discount_service.create_discount(db, data)


@router.post("/apply", response_model=ApplyDiscountResponse)
def apply_discount(data: ApplyDiscountRequest, db: Session = Depends(get_db)):
    discount = db.query(Discount).filter(Discount.id == data.discount_id).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found.")
    discount_amount = discount_service.calculate_discount_amount(data.subtotal, discount)
    return ApplyDiscountResponse(
        subtotal=data.subtotal,
        discount_amount=discount_amount,
        post_discount_price=data.subtotal - discount_amount,
    )
