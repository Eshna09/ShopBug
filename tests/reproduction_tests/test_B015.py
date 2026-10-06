"""
Reproduction test for B015.
Cart.jsx handleCheckout has an inverted ternary for discountId:

    BUG:
        const discountId = appliedDiscount
          ? null
          : KNOWN_DISCOUNTS.find(...)?.id

    CORRECT:
        const discountId = appliedDiscount
          ? KNOWN_DISCOUNTS.find(...)?.id
          : null

When a discount IS applied (appliedDiscount is truthy) the bug sends null,
so the checkout API receives no discount and the order total is wrong.
When NO discount is applied (appliedDiscount is falsy) the bug sends an ID,
adding an unexpected discount to an order that should have none.

This test mirrors the logic in Python to confirm both failure modes.
"""

KNOWN_DISCOUNTS = [
    {"id": 1, "code": "SAVE10"},
    {"id": 2, "code": "WELCOME20"},
]


def _discount_id_buggy(applied_discount, discount_code):
    """Replicates the buggy frontend ternary."""
    if applied_discount:
        return None
    return next(
        (d["id"] for d in KNOWN_DISCOUNTS if d["code"] == discount_code), None
    )


def _discount_id_correct(applied_discount, discount_code):
    """Correct implementation."""
    if applied_discount:
        return next(
            (d["id"] for d in KNOWN_DISCOUNTS if d["code"] == discount_code), None
        )
    return None


def test_B015_discount_applied_sends_null():
    """When a discount is applied, buggy code sends null (no discount to backend)."""
    applied = {"discount_amount": 10.0, "post_discount_price": 90.0}
    code = "SAVE10"

    buggy = _discount_id_buggy(applied, code)
    correct = _discount_id_correct(applied, code)

    assert correct == 1, f"Correct discountId should be 1, got {correct}"
    assert buggy is None, (
        f"Buggy discountId should be None (discount dropped), got {buggy}"
    )


def test_B015_no_discount_sends_id():
    """When no discount is applied, buggy code sends an ID (unexpected discount)."""
    applied = None
    code = "SAVE10"

    buggy = _discount_id_buggy(applied, code)
    correct = _discount_id_correct(applied, code)

    assert correct is None, f"Correct discountId with no discount should be None, got {correct}"
    assert buggy == 1, (
        f"Buggy discountId should be 1 (unexpected discount sent), got {buggy}"
    )
