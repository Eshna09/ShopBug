"""Reproduction test for B004 — zero quantity accepted in cart."""
import pytest
from app.database import Base
from app.models.product import Product
from app.services import cart_service
from tests.test_utils import engine, TestingSessionLocal


def test_B004():
    """Adding to cart with quantity=0 should raise HTTP 400."""
    from fastapi import HTTPException
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="B004Prod", category="Cat", price=10.0, stock=5, available=True)
        db.add(p)
        db.commit()
        db.refresh(p)
        try:
            cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=0)
            assert False, "Expected HTTP 400 for quantity=0"
        except HTTPException as exc:
            assert exc.status_code == 400
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
