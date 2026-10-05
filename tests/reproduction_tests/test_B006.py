"""Reproduction test for B006 — case-sensitive search."""
import pytest
from app.database import Base
from app.schemas.product import ProductCreate
from app.services import product_service
from tests.test_utils import engine, TestingSessionLocal


def test_B006():
    """Searching 'laptop' should find product named 'Laptop' (case-insensitive)."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        product_service.create_product(db, ProductCreate(name="Laptop", category="Electronics", price=500.0, stock=2))
        results = product_service.search_products(db, "laptop")
        assert len(results) > 0, "Expected to find 'Laptop' when searching 'laptop'"
        assert results[0].name == "Laptop"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
