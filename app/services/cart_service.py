from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.cart import CartItem
from app.models.product import Product


def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int) -> CartItem:
    if quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero.")
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    existing = db.query(CartItem).filter(
        CartItem.user_id == user_id, CartItem.product_id == product_id
    ).first()
    if existing:
        existing.quantity = quantity
        db.commit()
        db.refresh(existing)
        return existing
    item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def remove_from_cart(db: Session, user_id: int, product_id: int) -> None:
    item = db.query(CartItem).filter(
        CartItem.user_id == user_id, CartItem.product_id == product_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found.")
    db.delete(item)
    db.commit()


def update_cart_item(db: Session, user_id: int, product_id: int, quantity: int) -> CartItem:
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero.")
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    if quantity > product.stock:
        raise HTTPException(status_code=400, detail="Quantity exceeds available stock.")
    item = db.query(CartItem).filter(
        CartItem.user_id == user_id, CartItem.product_id == product_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found.")
    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item


def get_cart_items(db: Session, user_id: int) -> list[CartItem]:
    return db.query(CartItem).filter(CartItem.user_id == user_id).all()


def get_cart_subtotal(db: Session, user_id: int) -> float:
    items = get_cart_items(db, user_id)
    return sum(item.product.stock * item.quantity for item in items)
