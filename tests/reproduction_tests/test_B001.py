"""Reproduction test for B001 — discount apply_discount returns wrong value."""
import pytest
from app.database import Base
from app.models.order import Discount
from app.services import discount_service
from tests.test_utils import engine, TestingSessionLocal


def test_B001():
    """Applying 20% discount to 1000 should give post_discount of 800, not 200."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        discount = Discount(
            code="B001TEST",
            discount_percent=20.0,
            min_order_amount=0.0,
            max_discount_amount=None,
        )
        db.add(discount)
        db.commit()
        db.refresh(discount)
        result = discount_service.apply_discount(1000.0, discount)
        assert abs(result - 800.0) < 1e-4, f"Expected 800.0, got {result}"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
