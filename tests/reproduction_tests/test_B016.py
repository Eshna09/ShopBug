"""Reproduction test for B016 — order total_amount set to subtotal only."""
import os
import pytest
from app.database import Base
from app.models.product import Product
from app.services import cart_service, checkout_service
from tests.test_utils import engine, TestingSessionLocal

TAX_RATE = float(os.getenv("TAX_RATE", "0.10"))


def test_B016():
    """Order total_amount should be subtotal + tax, not just subtotal."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="B016Prod", category="Cat", price=100.0, stock=10, available=True)
        db.add(p)
        db.commit()
        db.refresh(p)
        cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=1)
        order = checkout_service.checkout(db, user_id=1)
        # subtotal=100, tax=10, total should be 110
        expected = 100.0 + (100.0 * TAX_RATE)
        assert abs(order.total_amount - expected) < 1e-4, f"Expected {expected}, got {order.total_amount}"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
