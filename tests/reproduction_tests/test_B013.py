"""Reproduction test for B013 — zero-stock product marked available."""
import pytest
from app.database import Base
from app.schemas.product import ProductCreate
from app.services import product_service
from tests.test_utils import engine, TestingSessionLocal


def test_B013():
    """Product with stock=0 should have available=False."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = product_service.create_product(db, ProductCreate(name="B013Prod", category="Cat", price=5.0, stock=0))
        assert p.available is False, f"Expected available=False for stock=0, got {p.available}"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
