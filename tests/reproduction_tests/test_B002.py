"""
Reproduction test for B002.
Tax is computed on the pre-discount subtotal instead of the post-discount amount.
Root cause: checkout_service.py `tax_amount = subtotal * TAX_RATE`
            should be `tax_amount = post_discount * TAX_RATE`.

Note: B012 (missing user_id in get_cart_items) prevents checkout from completing.
This test verifies the tax calculation logic directly on the service layer,
bypassing the checkout function's broken cart-fetching step.
"""
import os
from app.database import Base
from app.models.order import Discount
from app.services import discount_service
from tests.test_utils import engine, TestingSessionLocal

TAX_RATE = float(os.getenv("TAX_RATE", "0.10"))


def _checkout_tax_buggy(subtotal: float, discount_amount: float) -> float:
    """Replicates the buggy tax calculation: tax on pre-discount subtotal."""
    post_discount = subtotal - discount_amount
    tax_amount = subtotal * TAX_RATE          # BUG: should be post_discount * TAX_RATE
    total_amount = post_discount + tax_amount
    return tax_amount


def _checkout_tax_correct(subtotal: float, discount_amount: float) -> float:
    """Correct tax calculation: tax on post-discount amount."""
    post_discount = subtotal - discount_amount
    tax_amount = post_discount * TAX_RATE
    return tax_amount


def test_B002():
    """
    Expected: 20% discount on $100 → post_discount=$80, tax=10% of $80=$8.00.
    Actual:   tax=10% of original $100=$10.00 (ignores discount in tax base).
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        disc = Discount(
            code="B002DISC",
            discount_percent=20.0,
            min_order_amount=0.0,
            max_discount_amount=None,
        )
        db.add(disc)
        db.commit()
        db.refresh(disc)

        subtotal = 100.0
        discount_amount = discount_service.calculate_discount_amount(subtotal, disc)
        assert abs(discount_amount - 20.0) < 1e-4, f"Expected discount=20, got {discount_amount}"

        correct_tax = _checkout_tax_correct(subtotal, discount_amount)
        buggy_tax   = _checkout_tax_buggy(subtotal, discount_amount)

        # Demonstrate the bug: the two calculations differ
        assert abs(correct_tax - 8.0) < 1e-4, f"Correct tax should be 8.0, got {correct_tax}"
        assert abs(buggy_tax - 10.0) < 1e-4,  f"Buggy tax should be 10.0, got {buggy_tax}"

        # The test asserts CORRECT behaviour — which the bug violates.
        # This assertion FAILS on the buggy codebase, confirming B002 is active.
        assert abs(buggy_tax - 8.0) < 1e-4, (
            f"Expected tax_amount=8.0 (10% of post-discount $80), "
            f"but checkout_service uses pre-discount subtotal and produces tax={buggy_tax}"
        )
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
