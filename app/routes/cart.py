from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.cart import CartItemCreate, CartItemResponse, CartItemUpdate
from app.services import cart_service

router = APIRouter()


@router.post("/add", response_model=CartItemResponse, status_code=201)
def add_to_cart(data: CartItemCreate, db: Session = Depends(get_db)):
    return cart_service.add_to_cart(db, data.user_id, data.product_id, data.quantity)


@router.delete("/remove/{product_id}", status_code=200)
def remove_from_cart(product_id: int, user_id: int, db: Session = Depends(get_db)):
    cart_service.remove_from_cart(db, user_id, product_id)
    return {"message": "Item removed from cart."}


@router.put("/update", response_model=CartItemResponse)
def update_cart_item(data: CartItemUpdate, db: Session = Depends(get_db)):
    return cart_service.update_cart_item(db, data.user_id, data.product_id, data.quantity)


@router.get("/{user_id}", response_model=list[CartItemResponse])
def get_cart(user_id: int, db: Session = Depends(get_db)):
    return cart_service.get_cart_items(db, user_id)
