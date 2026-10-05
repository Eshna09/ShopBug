"""Reproduction test for B014 — discount cap check before percentage."""
import pytest
from app.database import Base
from app.models.order import Discount
from app.services import discount_service
from tests.test_utils import engine, TestingSessionLocal


def test_B014():
    """Discount where computed amount < cap should return computed amount, not cap."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # subtotal=30, percent=50, cap=20
        # Correct: 30*50/100=15, 15 < 20 → discount=15
        # Bug: subtotal(30) > cap(20) → returns 20 (wrong)
        discount = Discount(
            code="B014TEST", discount_percent=50.0,
            min_order_amount=0.0, max_discount_amount=20.0,
        )
        db.add(discount)
        db.commit()
        db.refresh(discount)
        amount = discount_service.calculate_discount_amount(30.0, discount)
        assert abs(amount - 15.0) < 1e-4, f"Expected 15.0, got {amount}"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
