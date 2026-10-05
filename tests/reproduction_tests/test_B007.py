"""Reproduction test for B007 — get_all_products returns unavailable products."""
import pytest
from app.database import Base
from app.schemas.product import ProductCreate
from app.services import product_service
from tests.test_utils import engine, TestingSessionLocal


def test_B007():
    """get_all_products should return available products, not unavailable ones."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        product_service.create_product(db, ProductCreate(name="Available", category="Cat", price=10.0, stock=5))
        results = product_service.get_all_products(db)
        assert len(results) > 0, "Expected at least one available product in results"
        assert any(p.name == "Available" for p in results)
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
