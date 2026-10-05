"""Reproduction test for B010 — empty cart guard inverted."""
import pytest
from app.database import Base
from app.models.product import Product
from app.services import cart_service, checkout_service
from tests.test_utils import engine, TestingSessionLocal


def test_B010():
    """Checkout with non-empty cart should succeed, not raise 400."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="B010Prod", category="Cat", price=10.0, stock=5, available=True)
        db.add(p)
        db.commit()
        db.refresh(p)
        cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=1)
        order = checkout_service.checkout(db, user_id=1)
        assert order is not None, "Expected checkout to succeed for non-empty cart"
    except Exception as exc:
        if "400" in str(exc) or "empty" in str(exc).lower():
            assert False, f"Checkout should succeed for non-empty cart, but got: {exc}"
        raise
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
