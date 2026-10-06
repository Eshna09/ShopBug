"""
Reproduction test for B014.
calculate_discount_amount compares subtotal against max_discount_amount
instead of comparing the computed discount (raw) against the cap.
"""
from app.database import Base
from app.models.order import Discount
from app.services import discount_service
from tests.test_utils import engine, TestingSessionLocal


def test_B014():
    """
    Expected: subtotal=30, percent=50%, cap=20 →
              raw=15, 15 < 20, so discount=15.
    Actual:   subtotal(30) > cap(20) triggers early return of 20 (the cap),
              ignoring that the correct raw amount is below the cap.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        disc = Discount(
            code="B014TEST",
            discount_percent=50.0,
            min_order_amount=0.0,
            max_discount_amount=20.0,
        )
        db.add(disc)
        db.commit()
        db.refresh(disc)

        amount = discount_service.calculate_discount_amount(30.0, disc)
        assert abs(amount - 15.0) < 1e-4, (
            f"Expected discount_amount=15.0 (50% of 30), got {amount}"
        )
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
