"""Reproduction test for B009 — cart subtotal uses stock instead of price."""
import pytest
from app.database import Base
from app.models.product import Product
from app.services import cart_service
from tests.test_utils import engine, TestingSessionLocal


def test_B009():
    """Cart subtotal should be price*qty (100*2=200), not stock*qty (5*2=10)."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="B009Prod", category="Cat", price=100.0, stock=5, available=True)
        db.add(p)
        db.commit()
        db.refresh(p)
        cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=2)
        subtotal = cart_service.get_cart_subtotal(db, user_id=1)
        assert abs(subtotal - 200.0) < 1e-4, f"Expected 200.0, got {subtotal}"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
