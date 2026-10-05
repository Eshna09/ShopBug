"""
Tests for product management — Requirements 3, 4, 5.
Covers unit tests and property-based tests (Properties 5–10 from design.md).
"""
import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from app.database import Base
from app.schemas.product import ProductCreate
from app.services import product_service
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
# Unit / example tests
# ---------------------------------------------------------------------------

def test_create_valid_product(client):
    resp = client.post("/products/", json={
        "name": "Laptop", "category": "Electronics", "price": 999.99, "stock": 5
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Laptop"
    assert data["price"] == 999.99
    assert data["available"] is True


def test_create_product_zero_price(client):
    resp = client.post("/products/", json={
        "name": "Freebie", "category": "Misc", "price": 0, "stock": 1
    })
    assert resp.status_code == 400


def test_create_product_negative_price(client):
    resp = client.post("/products/", json={
        "name": "Negative", "category": "Misc", "price": -5.0, "stock": 1
    })
    assert resp.status_code == 400


def test_create_product_negative_stock(client):
    resp = client.post("/products/", json={
        "name": "BadStock", "category": "Misc", "price": 10.0, "stock": -1
    })
    assert resp.status_code == 400


def test_get_product_by_id(client):
    created = client.post("/products/", json={
        "name": "Widget", "category": "Tools", "price": 25.0, "stock": 3
    })
    product_id = created.json()["id"]
    resp = client.get(f"/products/{product_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == product_id


def test_get_nonexistent_product(client):
    resp = client.get("/products/99999")
    assert resp.status_code == 404


def test_list_returns_only_available_products(client):
    client.post("/products/", json={
        "name": "Available", "category": "Cat", "price": 10.0, "stock": 5
    })
    client.post("/products/", json={
        "name": "Unavailable", "category": "Cat", "price": 10.0, "stock": 0
    })
    resp = client.get("/products/")
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()]
    assert "Available" in names
    assert "Unavailable" not in names


def test_search_case_insensitive(client):
    client.post("/products/", json={
        "name": "Laptop", "category": "Electronics", "price": 500.0, "stock": 2
    })
    resp = client.get("/products/search?q=laptop")
    assert resp.status_code == 200
    assert any(p["name"] == "Laptop" for p in resp.json())


def test_filter_by_category(client):
    client.post("/products/", json={
        "name": "Phone", "category": "Electronics", "price": 300.0, "stock": 4
    })
    client.post("/products/", json={
        "name": "Desk", "category": "Furniture", "price": 200.0, "stock": 2
    })
    resp = client.get("/products/filter?category=Electronics")
    assert resp.status_code == 200
    categories = [p["category"] for p in resp.json()]
    assert all(c == "Electronics" for c in categories)
    assert "Furniture" not in categories


def test_filter_unknown_category_returns_empty(client):
    resp = client.get("/products/filter?category=NonExistent")
    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------------------
# Property-based tests — call service layer directly
# ---------------------------------------------------------------------------

valid_names = st.text(min_size=1, max_size=50, alphabet=st.characters(
    whitelist_categories=("L", "N"), whitelist_characters=" -_"
))
valid_categories = st.sampled_from(["Electronics", "Furniture", "Clothing", "Books", "Tools"])
valid_prices = st.floats(min_value=0.01, max_value=10000.0, allow_nan=False, allow_infinity=False)
valid_stocks = st.integers(min_value=0, max_value=1000)


# Feature: shopbug, Property 5: Product Creation Round-Trip
# Validates: Requirements 3.1, 4.2
@given(
    name=valid_names,
    category=valid_categories,
    price=valid_prices,
    stock=valid_stocks,
)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_5_product_creation_round_trip(name, category, price, stock):
    """
    For any valid product payload, creating a product and retrieving it by ID
    SHALL return data equivalent to the creation payload.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        data = ProductCreate(name=name, category=category, price=price, stock=stock)
        created = product_service.create_product(db, data)
        fetched = product_service.get_product(db, created.id)
        assert fetched.name == name
        assert fetched.category == category
        assert abs(fetched.price - price) < 1e-6
        assert fetched.stock == stock
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Feature: shopbug, Property 6: Product Availability Mirrors Stock
# Validates: Requirements 3.4, 3.5
@given(
    name=valid_names,
    category=valid_categories,
    price=valid_prices,
    stock=valid_stocks,
)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_6_availability_mirrors_stock(name, category, price, stock):
    """
    After creation, the availability flag SHALL be True iff stock > 0.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        data = ProductCreate(name=name, category=category, price=price, stock=stock)
        created = product_service.create_product(db, data)
        assert created.available == (stock > 0)
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Feature: shopbug, Property 7: Invalid Price Rejection
# Validates: Requirements 3.2
@given(
    price=st.one_of(
        st.floats(max_value=0.0, allow_nan=False, allow_infinity=False),
        st.just(0.0),
        st.floats(min_value=-10000.0, max_value=-0.01, allow_nan=False, allow_infinity=False),
    )
)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_7_invalid_price_rejection(price):
    """
    For any price <= 0, product creation SHALL raise HTTP 400.
    """
    from fastapi import HTTPException
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        data = ProductCreate(name="Test", category="Cat", price=price, stock=1)
        try:
            product_service.create_product(db, data)
            assert False, f"Expected HTTP 400 for price={price}"
        except HTTPException as exc:
            assert exc.status_code == 400
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Feature: shopbug, Property 8: List Products Returns Only Available
# Validates: Requirements 4.1
@given(
    stocks=st.lists(st.integers(min_value=0, max_value=100), min_size=1, max_size=8),
)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_8_list_only_available(stocks):
    """
    get_all_products SHALL return only products with available=True.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        for i, stock in enumerate(stocks):
            data = ProductCreate(name=f"Prod{i}", category="Cat", price=1.0, stock=stock)
            product_service.create_product(db, data)
        results = product_service.get_all_products(db)
        assert all(p.available is True for p in results)
        expected_available = sum(1 for s in stocks if s > 0)
        assert len(results) == expected_available
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Feature: shopbug, Property 9: Case-Insensitive Search
# Validates: Requirements 5.1
@given(
    base_name=st.text(
        min_size=2,
        max_size=20,
        alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    ),
)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_9_case_insensitive_search(base_name):
    """
    Search with varied case SHALL find the product.
    ASCII letters only — avoids multi-char Unicode uppercase edge cases
    (e.g. 'ß'.upper() == 'SS') that SQLite ILIKE does not handle.
    """
    if not base_name.strip():
        return
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        data = ProductCreate(name=base_name, category="Cat", price=1.0, stock=1)
        product_service.create_product(db, data)
        query = base_name.upper()
        results = product_service.search_products(db, query)
        assert any(p.name == base_name for p in results), (
            f"Expected to find '{base_name}' when searching '{query}'"
        )
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Feature: shopbug, Property 10: Category Filter Exactness
# Validates: Requirements 5.2
@given(
    target_category=valid_categories,
    other_category=valid_categories,
    n_target=st.integers(min_value=1, max_value=4),
    n_other=st.integers(min_value=1, max_value=4),
)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_10_category_filter_exactness(target_category, other_category, n_target, n_other):
    """
    filter_by_category SHALL return exactly the products in that category.
    """
    if target_category == other_category:
        return
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        for i in range(n_target):
            product_service.create_product(db, ProductCreate(
                name=f"Target{i}", category=target_category, price=1.0, stock=1
            ))
        for i in range(n_other):
            product_service.create_product(db, ProductCreate(
                name=f"Other{i}", category=other_category, price=1.0, stock=1
            ))
        results = product_service.filter_by_category(db, target_category)
        assert all(p.category == target_category for p in results)
        assert len(results) == n_target
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
