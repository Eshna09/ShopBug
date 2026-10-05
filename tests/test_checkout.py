"""
Tests for checkout — Requirement 9.
Covers unit tests and property-based tests (Properties 14 and 15 from design.md).
"""
import os
import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from app.database import Base
from app.models.product import Product
from app.models.order import Discount
from app.schemas.order import DiscountCreate
from app.schemas.product import ProductCreate
from app.services import cart_service, checkout_service, product_service, discount_service
from tests.test_utils import engine, TestingSessionLocal

# conftest.py provides autouse setup_db, client, and db_session fixtures.

TAX_RATE = float(os.getenv("TAX_RATE", "0.10"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_product(db, name="TestProduct", price=100.0, stock=50):
    p = Product(name=name, category="General", price=price, stock=stock, available=stock > 0)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _create_discount(db, code="DISC10", percent=10.0, min_amt=0.0, cap=None):
    d = Discount(code=code, discount_percent=percent, min_order_amount=min_amt, max_discount_amount=cap)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


# ---------------------------------------------------------------------------
# Unit / example tests
# ---------------------------------------------------------------------------

def test_checkout_happy_path(client, db_session):
    p = _create_product(db_session, price=50.0, stock=10)
    cart_service.add_to_cart(db_session, user_id=1, product_id=p.id, quantity=2)
    resp = client.post("/checkout/?user_id=1")
    assert resp.status_code == 201
    data = resp.json()
    assert data["user_id"] == 1
    expected_subtotal = 100.0
    expected_tax = expected_subtotal * TAX_RATE
    expected_total = expected_subtotal + expected_tax
    assert abs(data["subtotal"] - expected_subtotal) < 1e-4
    assert abs(data["total_amount"] - expected_total) < 1e-4


def test_checkout_with_discount(client, db_session):
    p = _create_product(db_session, price=100.0, stock=5)
    d = _create_discount(db_session, code="20OFF", percent=20.0)
    cart_service.add_to_cart(db_session, user_id=2, product_id=p.id, quantity=1)
    resp = client.post(f"/checkout/?user_id=2&discount_id={d.id}")
    assert resp.status_code == 201
    data = resp.json()
    # subtotal=100, discount=20, post_discount=80, tax=8, total=88
    assert abs(data["discount_amount"] - 20.0) < 1e-4
    assert abs(data["total_amount"] - 88.0) < 1e-4


def test_checkout_empty_cart(client):
    resp = client.post("/checkout/?user_id=99")
    assert resp.status_code == 400
    assert "empty" in resp.json()["detail"].lower()


def test_checkout_insufficient_stock(client, db_session):
    p = _create_product(db_session, price=10.0, stock=1)
    cart_service.add_to_cart(db_session, user_id=3, product_id=p.id, quantity=1)
    # Manually reduce stock to 0 to simulate depletion between add and checkout
    p.stock = 0
    db_session.commit()
    resp = client.post("/checkout/?user_id=3")
    assert resp.status_code == 400
    assert "stock" in resp.json()["detail"].lower()


def test_checkout_stock_decremented(db_session):
    p = _create_product(db_session, price=20.0, stock=10)
    cart_service.add_to_cart(db_session, user_id=4, product_id=p.id, quantity=3)
    checkout_service.checkout(db_session, user_id=4)
    db_session.refresh(p)
    assert p.stock == 7


def test_checkout_total_correct(db_session):
    p = _create_product(db_session, price=200.0, stock=5)
    cart_service.add_to_cart(db_session, user_id=5, product_id=p.id, quantity=2)
    order = checkout_service.checkout(db_session, user_id=5)
    subtotal = 400.0
    tax = subtotal * TAX_RATE
    total = subtotal + tax
    assert abs(order.subtotal - subtotal) < 1e-4
    assert abs(order.tax_amount - tax) < 1e-4
    assert abs(order.total_amount - total) < 1e-4


def test_checkout_stock_exactly_equals_quantity(db_session):
    """Checkout succeeds when stock exactly equals requested quantity."""
    p = _create_product(db_session, price=15.0, stock=3)
    cart_service.add_to_cart(db_session, user_id=6, product_id=p.id, quantity=3)
    order = checkout_service.checkout(db_session, user_id=6)
    assert order is not None
    db_session.refresh(p)
    assert p.stock == 0
    assert p.available is False


def test_checkout_invalid_discount(client, db_session):
    p = _create_product(db_session, price=50.0, stock=5)
    cart_service.add_to_cart(db_session, user_id=7, product_id=p.id, quantity=1)
    resp = client.post("/checkout/?user_id=7&discount_id=99999")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Property-based tests — call service layer directly
# ---------------------------------------------------------------------------

positive_price = st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False)
positive_stock = st.integers(min_value=1, max_value=50)
positive_qty = st.integers(min_value=1, max_value=10)


# Feature: shopbug, Property 14: Checkout Final Total Formula
# Validates: Requirements 9.4, 9.5
@given(
    price=positive_price,
    qty=positive_qty,
    discount_percent=st.floats(min_value=0.01, max_value=99.99, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_14_checkout_total_formula(price, qty, discount_percent):
    """
    For any non-empty cart with subtotal S, discount D, and tax rate T,
    the Order total SHALL equal (S - D) + (S - D) * T.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Ensure enough stock
        stock = max(qty + 5, 10)
        p = Product(name="CheckProd", category="Cat", price=price, stock=stock, available=True)
        db.add(p)
        d = Discount(
            code="P14DISC",
            discount_percent=discount_percent,
            min_order_amount=0.0,
            max_discount_amount=None,
        )
        db.add(d)
        db.commit()
        db.refresh(p)
        db.refresh(d)

        user_id = 500
        cart_service.add_to_cart(db, user_id=user_id, product_id=p.id, quantity=qty)
        order = checkout_service.checkout(db, user_id=user_id, discount_id=d.id)

        subtotal = price * qty
        discount_amount = subtotal * discount_percent / 100.0
        post_discount = subtotal - discount_amount
        expected_tax = post_discount * TAX_RATE
        expected_total = post_discount + expected_tax

        assert abs(order.total_amount - expected_total) < 1e-2, (
            f"Expected total {expected_total}, got {order.total_amount}"
        )
        assert abs(order.tax_amount - expected_tax) < 1e-2, (
            f"Expected tax {expected_tax}, got {order.tax_amount}"
        )
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Feature: shopbug, Property 15: Stock Decrement After Checkout
# Validates: Requirements 9.6
@given(
    price=positive_price,
    stock=positive_stock,
    qty=positive_qty,
)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_15_stock_decrement(price, stock, qty):
    """
    After checkout, each product's stock SHALL equal pre-checkout stock minus qty.
    """
    if qty > stock:
        return  # skip: add_to_cart would reject it too

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="StockProd", category="Cat", price=price, stock=stock, available=True)
        db.add(p)
        db.commit()
        db.refresh(p)

        user_id = 600
        cart_service.add_to_cart(db, user_id=user_id, product_id=p.id, quantity=qty)
        checkout_service.checkout(db, user_id=user_id)

        db.refresh(p)
        assert p.stock == stock - qty, (
            f"Expected stock {stock - qty}, got {p.stock}"
        )
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
