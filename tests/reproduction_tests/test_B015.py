"""Reproduction test for B015 — stock check removed from add_to_cart."""
import pytest
from app.database import Base
from app.models.product import Product
from app.services import cart_service
from tests.test_utils import engine, TestingSessionLocal


def test_B015():
    """Adding quantity > stock to cart should raise HTTP 400."""
    from fastapi import HTTPException
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="B015Prod", category="Cat", price=10.0, stock=3, available=True)
        db.add(p)
        db.commit()
        db.refresh(p)
        try:
            cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=5)
            assert False, "Expected HTTP 400 for quantity > stock"
        except HTTPException as exc:
            assert exc.status_code == 400
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
