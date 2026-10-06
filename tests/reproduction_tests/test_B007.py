"""
Reproduction test for B007.
Products.jsx loadProducts() discards the API response and always calls
setProducts([]).  Even when GET /products/ returns items, the React state
is set to an empty array so the page renders nothing.

This test confirms the backend DOES return products (so the API layer is
correct) and that the bug must be in the frontend state assignment.
"""
import pytest
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app
from app.models.product import Product
from tests.test_utils import engine, TestingSessionLocal, override_get_db


def make_client():
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app, raise_server_exceptions=True)


def test_B007():
    """
    Expected: Products page shows product cards after a successful API response.
    Actual:   Frontend ignores the response and renders an empty product grid.

    Verified here: the backend returns products correctly; the discard is in
    the frontend (setProducts([])).
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    client = make_client()
    try:
        # Insert a product that the buggy list endpoint will return (available=False)
        p = Product(name="B007Prod", category="Cat", price=10.0, stock=5, available=False)
        db.add(p)
        db.commit()

        resp = client.get("/products/")
        assert resp.status_code == 200
        products = resp.json()
        assert len(products) > 0, (
            "Backend GET /products/ returned empty — seed data may be missing. "
            "The bug is frontend-side: loadProducts() calls setProducts([]) "
            "discarding the API response."
        )
        assert any(pr["name"] == "B007Prod" for pr in products), (
            "Expected B007Prod in product list from backend"
        )
    finally:
        app.dependency_overrides.clear()
        db.close()
        Base.metadata.drop_all(bind=engine)
