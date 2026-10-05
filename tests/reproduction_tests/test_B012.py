"""Reproduction test for B012 — checkout calls get_cart_items without user_id."""
import pytest
from app.database import Base
from app.models.product import Product
from app.services import cart_service, checkout_service
from tests.test_utils import engine, TestingSessionLocal


def test_B012():
    """Checkout should succeed without TypeError (get_cart_items must receive user_id)."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="B012Prod", category="Cat", price=10.0, stock=5, available=True)
        db.add(p)
        db.commit()
        db.refresh(p)
        cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=1)
        try:
            order = checkout_service.checkout(db, user_id=1)
            assert order is not None, "Expected checkout to succeed"
        except TypeError:
            assert False, "Checkout raised TypeError — get_cart_items called without user_id"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
