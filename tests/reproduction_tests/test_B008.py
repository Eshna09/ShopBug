"""Reproduction test for B008 — discount at minimum boundary rejected."""
import pytest
from app.database import Base
from app.models.order import Discount
from app.services import discount_service
from tests.test_utils import engine, TestingSessionLocal


def test_B008():
    """Discount at exactly min_order_amount should apply (subtotal == min)."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        discount = Discount(
            code="B008TEST", discount_percent=10.0,
            min_order_amount=500.0, max_discount_amount=None,
        )
        db.add(discount)
        db.commit()
        db.refresh(discount)
        amount = discount_service.calculate_discount_amount(500.0, discount)
        assert amount > 0, f"Expected discount > 0 at exact minimum, got {amount}"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
