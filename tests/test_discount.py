"""
Tests for discount system — Requirement 8.
Covers unit tests and property-based test (Property 13 from design.md).
"""
import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from app.database import Base
from app.models.order import Discount
from app.schemas.order import DiscountCreate
from app.services import discount_service
from tests.test_utils import engine, TestingSessionLocal

# conftest.py provides autouse setup_db, client, and db_session fixtures.


# ---------------------------------------------------------------------------
# Unit / example tests
# ---------------------------------------------------------------------------

def test_create_discount_success(client):
    resp = client.post("/discounts/create", json={
        "code": "SAVE10", "discount_percent": 10.0, "min_order_amount": 0.0
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == "SAVE10"
    assert data["discount_percent"] == 10.0


def test_create_discount_zero_percent(client):
    resp = client.post("/discounts/create", json={
        "code": "ZERO", "discount_percent": 0.0, "min_order_amount": 0.0
    })
    assert resp.status_code == 400


def test_create_discount_100_percent(client):
    resp = client.post("/discounts/create", json={
        "code": "FULL", "discount_percent": 100.0, "min_order_amount": 0.0
    })
    assert resp.status_code == 400


def test_create_discount_negative_percent(client):
    resp = client.post("/discounts/create", json={
        "code": "NEG", "discount_percent": -5.0, "min_order_amount": 0.0
    })
    assert resp.status_code == 400


def test_apply_discount_basic(client):
    create_resp = client.post("/discounts/create", json={
        "code": "TENOFF", "discount_percent": 10.0, "min_order_amount": 0.0
    })
    discount_id = create_resp.json()["id"]
    resp = client.post("/discounts/apply", json={"subtotal": 100.0, "discount_id": discount_id})
    assert resp.status_code == 200
    data = resp.json()
    assert abs(data["discount_amount"] - 10.0) < 1e-6
    assert abs(data["post_discount_price"] - 90.0) < 1e-6


def test_apply_discount_below_minimum(client):
    create_resp = client.post("/discounts/create", json={
        "code": "MINAMT", "discount_percent": 20.0, "min_order_amount": 50.0
    })
    discount_id = create_resp.json()["id"]
    resp = client.post("/discounts/apply", json={"subtotal": 30.0, "discount_id": discount_id})
    assert resp.status_code == 200
    data = resp.json()
    assert data["discount_amount"] == 0.0
    assert abs(data["post_discount_price"] - 30.0) < 1e-6


def test_apply_discount_at_minimum(client):
    """Subtotal exactly at min_order_amount → discount applies."""
    create_resp = client.post("/discounts/create", json={
        "code": "ATMIN", "discount_percent": 10.0, "min_order_amount": 50.0
    })
    discount_id = create_resp.json()["id"]
    resp = client.post("/discounts/apply", json={"subtotal": 50.0, "discount_id": discount_id})
    assert resp.status_code == 200
    data = resp.json()
    assert abs(data["discount_amount"] - 5.0) < 1e-6


def test_apply_discount_with_cap(client):
    """Computed discount exceeds cap → discount equals cap."""
    create_resp = client.post("/discounts/create", json={
        "code": "CAPPED", "discount_percent": 50.0, "min_order_amount": 0.0,
        "max_discount_amount": 20.0
    })
    discount_id = create_resp.json()["id"]
    resp = client.post("/discounts/apply", json={"subtotal": 200.0, "discount_id": discount_id})
    assert resp.status_code == 200
    data = resp.json()
    # 50% of 200 = 100, but capped at 20
    assert abs(data["discount_amount"] - 20.0) < 1e-6
    assert abs(data["post_discount_price"] - 180.0) < 1e-6


def test_apply_nonexistent_discount(client):
    resp = client.post("/discounts/apply", json={"subtotal": 100.0, "discount_id": 99999})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Property-based tests — call service layer directly
# ---------------------------------------------------------------------------

valid_percent = st.floats(min_value=0.01, max_value=99.99, allow_nan=False, allow_infinity=False)
valid_subtotal = st.floats(min_value=0.01, max_value=100000.0, allow_nan=False, allow_infinity=False)
valid_min_order = st.floats(min_value=0.0, max_value=500.0, allow_nan=False, allow_infinity=False)
optional_cap = st.one_of(
    st.none(),
    st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False),
)


# Feature: shopbug, Property 13: Discount Arithmetic Correctness
# Validates: Requirements 8.1, 8.2, 8.3, 8.6
@given(
    subtotal=valid_subtotal,
    discount_percent=valid_percent,
    min_order_amount=valid_min_order,
    max_discount_amount=optional_cap,
)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_13_discount_arithmetic(subtotal, discount_percent, min_order_amount, max_discount_amount):
    """
    For any subtotal S, discount % P, optional min M, and optional cap C:
    - if S < M: discount_amount = 0
    - else: discount_amount = min(S*P/100, C) when C set, else S*P/100
    - post_discount_price = S - discount_amount
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Build an in-memory Discount object (not persisted — pure arithmetic test)
        discount = Discount(
            code="PROP13",
            discount_percent=discount_percent,
            min_order_amount=min_order_amount,
            max_discount_amount=max_discount_amount,
        )

        discount_amount = discount_service.calculate_discount_amount(subtotal, discount)
        post_discount = discount_service.apply_discount(subtotal, discount)

        if subtotal < min_order_amount:
            assert discount_amount == 0.0, (
                f"Below min: expected 0.0 discount, got {discount_amount}"
            )
        else:
            raw = subtotal * discount_percent / 100.0
            if max_discount_amount is not None:
                expected_discount = min(raw, max_discount_amount)
            else:
                expected_discount = raw
            assert abs(discount_amount - expected_discount) < 1e-4, (
                f"Expected discount {expected_discount}, got {discount_amount}"
            )

        assert abs(post_discount - (subtotal - discount_amount)) < 1e-4, (
            f"post_discount mismatch: {post_discount} != {subtotal} - {discount_amount}"
        )
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
