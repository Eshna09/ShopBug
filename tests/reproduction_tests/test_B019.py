"""Reproduction test for B019 — stock not decremented after checkout."""
import pytest
from app.database import Base
from app.models.product import Product
from app.services import cart_service, checkout_service
from tests.test_utils import engine, TestingSessionLocal


def test_B019():
    """After checkout, product stock should be decremented by purchased quantity."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="B019Prod", category="Cat", price=10.0, stock=5, available=True)
        db.add(p)
        db.commit()
        db.refresh(p)
        cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=2)
        checkout_service.checkout(db, user_id=1)
        db.refresh(p)
        assert p.stock == 3, f"Expected stock 3 after buying 2, got {p.stock}"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
