"""Reproduction test for B017 — category filter returns non-matching products."""
import pytest
from app.database import Base
from app.schemas.product import ProductCreate
from app.services import product_service
from tests.test_utils import engine, TestingSessionLocal


def test_B017():
    """Filtering by 'Electronics' should return only Electronics products."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        product_service.create_product(db, ProductCreate(name="Phone", category="Electronics", price=100.0, stock=1))
        product_service.create_product(db, ProductCreate(name="Novel", category="Books", price=20.0, stock=1))
        results = product_service.filter_by_category(db, "Electronics")
        assert len(results) == 1, f"Expected 1 Electronics product, got {len(results)}"
        assert results[0].category == "Electronics"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
