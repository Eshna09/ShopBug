"""
Edge-case and boundary tests spanning all modules.
"""
import os
import pytest
from fastapi.testclient import TestClient

from app.models.product import Product
from app.models.order import Discount
from app.services import cart_service, checkout_service, product_service
from app.schemas.product import ProductCreate
from tests.test_utils import TestingSessionLocal

# conftest.py provides autouse setup_db, client, and db_session fixtures.

TAX_RATE = float(os.getenv("TAX_RATE", "0.10"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_product(db, name="Edge", price=10.0, stock=0):
    p = Product(name=name, category="EdgeCat", price=price, stock=stock, available=stock > 0)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _make_discount(db, code="EDGE", percent=10.0, min_amt=0.0, cap=None):
    d = Discount(code=code, discount_percent=percent, min_order_amount=min_amt, max_discount_amount=cap)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


# ---------------------------------------------------------------------------
# Edge cases: availability
# ---------------------------------------------------------------------------

def test_stock_zero_product_available_false(db_session):
    """A product created with stock=0 SHALL have available=False."""
    data = ProductCreate(name="ZeroStock", category="Cat", price=5.0, stock=0)
    p = product_service.create_product(db_session, data)
    assert p.available is False


def test_stock_zero_product_not_in_list(client, db_session):
    """A product with stock=0 SHALL NOT appear in the list_products endpoint."""
    # Create one available and one zero-stock product
    _make_product(db_session, name="InStock", price=5.0, stock=3)
    _make_product(db_session, name="OutOfStock", price=5.0, stock=0)

    resp = client.get("/products/")
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()]
    assert "InStock" in names
    assert "OutOfStock" not in names


# ---------------------------------------------------------------------------
# Edge cases: cart
# ---------------------------------------------------------------------------

def test_add_cart_item_qty_exceeds_stock(client, db_session):
    """Add cart item with qty > stock → 400."""
    p = _make_product(db_session, name="LowStock", price=10.0, stock=2)
    resp = client.post("/cart/add", json={"user_id": 1, "product_id": p.id, "quantity": 5})
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Edge cases: discount
# ---------------------------------------------------------------------------

def test_discount_at_min_order_amount(db_session):
    """Subtotal exactly at min_order_amount → discount applies."""
    d = _make_discount(db_session, code="EXACT50", percent=10.0, min_amt=50.0)
    from app.services.discount_service import calculate_discount_amount
    amount = calculate_discount_amount(50.0, d)
    assert abs(amount - 5.0) < 1e-6, f"Expected 5.0 but got {amount}"


def test_discount_cap_limits_discount(db_session):
    """Computed discount exceeds cap → discount equals cap."""
    d = _make_discount(db_session, code="CAPLIMIT", percent=50.0, min_amt=0.0, cap=15.0)
    from app.services.discount_service import calculate_discount_amount
    # 50% of 100 = 50, but capped at 15
    amount = calculate_discount_amount(100.0, d)
    assert abs(amount - 15.0) < 1e-6, f"Expected 15.0 (cap) but got {amount}"


# ---------------------------------------------------------------------------
# Edge cases: checkout
# ---------------------------------------------------------------------------

def test_checkout_stock_exactly_equals_qty(db_session):
    """Checkout succeeds when stock exactly equals requested quantity."""
    p = _make_product(db_session, name="ExactStock", price=20.0, stock=4)
    cart_service.add_to_cart(db_session, user_id=10, product_id=p.id, quantity=4)
    order = checkout_service.checkout(db_session, user_id=10)
    assert order is not None


def test_checkout_stock_decremented_to_zero_available_false(db_session):
    """After checkout, stock decremented to 0 → product.available = False."""
    p = _make_product(db_session, name="DepleteProd", price=25.0, stock=2)
    cart_service.add_to_cart(db_session, user_id=11, product_id=p.id, quantity=2)
    checkout_service.checkout(db_session, user_id=11)
    db_session.refresh(p)
    assert p.stock == 0
    assert p.available is False
