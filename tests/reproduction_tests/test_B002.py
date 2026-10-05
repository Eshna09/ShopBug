"""Reproduction test for B002 — tax calculated on pre-discount subtotal."""
import os
import pytest
from app.database import Base
from app.models.product import Product
from app.models.order import Discount
from app.services import cart_service, checkout_service
from tests.test_utils import engine, TestingSessionLocal

TAX_RATE = float(os.getenv("TAX_RATE", "0.10"))


def test_B002():
    """Tax should be on post-discount amount (80*0.10=8.0), not pre-discount (100*0.10=10.0)."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="B002Prod", category="Cat", price=100.0, stock=10, available=True)
        d = Discount(code="B002DISC", discount_percent=20.0, min_order_amount=0.0, max_discount_amount=None)
        db.add_all([p, d])
        db.commit()
        db.refresh(p)
        db.refresh(d)
        cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=1)
        order = checkout_service.checkout(db, user_id=1, discount_id=d.id)
        # subtotal=100, discount=20, post_discount=80, tax should be 80*0.10=8.0
        assert abs(order.tax_amount - 8.0) < 1e-4, f"Expected tax 8.0, got {order.tax_amount}"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
