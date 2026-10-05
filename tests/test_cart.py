"""
Tests for shopping cart — Requirements 6 and 7.
Covers unit tests and property-based tests (Properties 11, 12, 16 from design.md).
"""
import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from app.database import Base
from app.models.product import Product
from app.schemas.product import ProductCreate
from app.services import cart_service, product_service
from tests.test_utils import engine, TestingSessionLocal

# conftest.py provides autouse setup_db, client, and db_session fixtures.


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_product(db, name="Widget", price=10.0, stock=100):
    """Create and persist a product, return its id."""
    p = Product(name=name, category="General", price=price, stock=stock, available=stock > 0)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p.id


# ---------------------------------------------------------------------------
# Unit / example tests
# ---------------------------------------------------------------------------

def test_add_to_cart_success(client, db_session):
    pid = _make_product(db_session)
    resp = client.post("/cart/add", json={"user_id": 1, "product_id": pid, "quantity": 2})
    assert resp.status_code == 201
    data = resp.json()
    assert data["quantity"] == 2
    assert data["product_id"] == pid


def test_add_to_cart_zero_quantity(client, db_session):
    pid = _make_product(db_session)
    resp = client.post("/cart/add", json={"user_id": 1, "product_id": pid, "quantity": 0})
    assert resp.status_code == 400


def test_add_to_cart_negative_quantity(client, db_session):
    pid = _make_product(db_session)
    resp = client.post("/cart/add", json={"user_id": 1, "product_id": pid, "quantity": -3})
    assert resp.status_code == 400


def test_add_to_cart_exceeds_stock(client, db_session):
    pid = _make_product(db_session, stock=5)
    resp = client.post("/cart/add", json={"user_id": 1, "product_id": pid, "quantity": 10})
    assert resp.status_code == 400


def test_add_to_cart_nonexistent_product(client):
    resp = client.post("/cart/add", json={"user_id": 1, "product_id": 99999, "quantity": 1})
    assert resp.status_code == 404


def test_add_to_cart_updates_existing_item(client, db_session):
    pid = _make_product(db_session, stock=50)
    client.post("/cart/add", json={"user_id": 1, "product_id": pid, "quantity": 3})
    resp = client.post("/cart/add", json={"user_id": 1, "product_id": pid, "quantity": 7})
    assert resp.status_code == 201
    assert resp.json()["quantity"] == 7


def test_remove_from_cart(client, db_session):
    pid = _make_product(db_session, stock=10)
    client.post("/cart/add", json={"user_id": 1, "product_id": pid, "quantity": 2})
    resp = client.delete(f"/cart/remove/{pid}?user_id=1")
    assert resp.status_code == 200
    # Cart should now be empty
    items_resp = client.get("/cart/1")
    assert items_resp.json() == []


def test_remove_nonexistent_cart_item(client):
    resp = client.delete("/cart/remove/99999?user_id=1")
    assert resp.status_code == 404


def test_update_cart_item(client, db_session):
    pid = _make_product(db_session, stock=20)
    client.post("/cart/add", json={"user_id": 1, "product_id": pid, "quantity": 2})
    resp = client.put("/cart/update", json={"user_id": 1, "product_id": pid, "quantity": 5})
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 5


def test_update_cart_item_zero_quantity(client, db_session):
    pid = _make_product(db_session, stock=20)
    client.post("/cart/add", json={"user_id": 1, "product_id": pid, "quantity": 2})
    resp = client.put("/cart/update", json={"user_id": 1, "product_id": pid, "quantity": 0})
    assert resp.status_code == 400


def test_get_cart_items(client, db_session):
    pid = _make_product(db_session, stock=10)
    client.post("/cart/add", json={"user_id": 42, "product_id": pid, "quantity": 3})
    resp = client.get("/cart/42")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["quantity"] == 3


def test_empty_cart_returns_empty_list(client):
    resp = client.get("/cart/999")
    assert resp.status_code == 200
    assert resp.json() == []


def test_cart_subtotal_correct(db_session):
    """Subtotal = sum of price * quantity for each item."""
    pid1 = _make_product(db_session, name="A", price=10.0, stock=20)
    pid2 = _make_product(db_session, name="B", price=5.0, stock=20)
    cart_service.add_to_cart(db_session, user_id=1, product_id=pid1, quantity=3)
    cart_service.add_to_cart(db_session, user_id=1, product_id=pid2, quantity=4)
    subtotal = cart_service.get_cart_subtotal(db_session, user_id=1)
    assert abs(subtotal - (10.0 * 3 + 5.0 * 4)) < 1e-6


# ---------------------------------------------------------------------------
# Property-based tests — call service layer directly
# ---------------------------------------------------------------------------

positive_qty = st.integers(min_value=1, max_value=50)
non_positive_qty = st.integers(max_value=0)


# Feature: shopbug, Property 11: Cart Subtotal Formula
# Validates: Requirements 7.1
@given(
    items=st.lists(
        st.tuples(
            st.floats(min_value=0.01, max_value=500.0, allow_nan=False, allow_infinity=False),
            st.integers(min_value=1, max_value=50),
        ),
        min_size=1,
        max_size=6,
    )
)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_11_cart_subtotal_formula(items):
    """
    For any cart with N items, subtotal SHALL equal sum(price_i * quantity_i).
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        user_id = 1
        expected = 0.0
        for i, (price, qty) in enumerate(items):
            p = Product(name=f"P{i}", category="Cat", price=price, stock=qty + 10, available=True)
            db.add(p)
            db.commit()
            db.refresh(p)
            cart_service.add_to_cart(db, user_id=user_id, product_id=p.id, quantity=qty)
            expected += price * qty
        subtotal = cart_service.get_cart_subtotal(db, user_id)
        assert abs(subtotal - expected) < 1e-4, f"Expected {expected}, got {subtotal}"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Feature: shopbug, Property 12: Invalid Cart Quantity Rejection
# Validates: Requirements 6.2
@given(qty=non_positive_qty)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_12_invalid_quantity_rejection(qty):
    """
    For any quantity <= 0, add_to_cart SHALL raise HTTP 400 and the cart
    SHALL remain unchanged.
    """
    from fastapi import HTTPException
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="TestProd", category="Cat", price=5.0, stock=100, available=True)
        db.add(p)
        db.commit()
        db.refresh(p)
        try:
            cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=qty)
            assert False, f"Expected HTTP 400 for qty={qty}"
        except HTTPException as exc:
            assert exc.status_code == 400
        items = cart_service.get_cart_items(db, user_id=1)
        assert len(items) == 0
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Feature: shopbug, Property 16: Cart User Isolation
# Validates: Requirements 6.6, 9.7
@given(
    qty_u1=st.integers(min_value=1, max_value=20),
    qty_u2=st.integers(min_value=1, max_value=20),
)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_16_cart_user_isolation(qty_u1, qty_u2):
    """
    Retrieving cart items for user U1 SHALL return only U1's items and NOT
    include any item belonging to U2.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p1 = Product(name="ProdU1", category="Cat", price=1.0, stock=100, available=True)
        p2 = Product(name="ProdU2", category="Cat", price=2.0, stock=100, available=True)
        db.add_all([p1, p2])
        db.commit()
        db.refresh(p1)
        db.refresh(p2)

        user1_id, user2_id = 101, 202
        cart_service.add_to_cart(db, user_id=user1_id, product_id=p1.id, quantity=qty_u1)
        cart_service.add_to_cart(db, user_id=user2_id, product_id=p2.id, quantity=qty_u2)

        u1_items = cart_service.get_cart_items(db, user_id=user1_id)
        u2_items = cart_service.get_cart_items(db, user_id=user2_id)

        assert all(item.user_id == user1_id for item in u1_items)
        assert all(item.user_id == user2_id for item in u2_items)

        u1_product_ids = {item.product_id for item in u1_items}
        u2_product_ids = {item.product_id for item in u2_items}
        assert u1_product_ids.isdisjoint(u2_product_ids)
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
