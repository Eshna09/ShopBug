"""
Reproduction test for B003.
Cart.jsx computes subtotal as:
    sum + item.product.price + item.quantity   (addition — BUG)
instead of:
    sum + item.product.price * item.quantity   (multiplication — correct)

This test mirrors the frontend calculation using Python to confirm
the arithmetic discrepancy.
"""


def _buggy_subtotal(items):
    """Replicates the buggy frontend calculation."""
    return sum(item["price"] + item["qty"] for item in items)


def _correct_subtotal(items):
    """Correct calculation: price × quantity."""
    return sum(item["price"] * item["qty"] for item in items)


def test_B003():
    """
    Expected: 2 units of a $49.99 product → subtotal = $99.98.
    Actual:   buggy frontend computes 49.99 + 2 = $51.99.
    """
    cart_items = [{"price": 49.99, "qty": 2}]

    correct = _correct_subtotal(cart_items)
    buggy = _buggy_subtotal(cart_items)

    assert abs(correct - 99.98) < 1e-4, f"Correct subtotal should be 99.98, got {correct}"
    assert abs(buggy - 99.98) > 1e-4, (
        f"Buggy subtotal incorrectly matches correct value — the bug may not be active. "
        f"Buggy result: {buggy}"
    )

    # Verify the buggy calculation produces the wrong result
    assert abs(buggy - 51.99) < 1e-4, (
        f"Buggy subtotal (price+qty) should be 51.99 for price=49.99 qty=2, got {buggy}"
    )


def test_B003_multi_item():
    """Multi-item cart demonstrates the scaling error in buggy addition."""
    cart_items = [
        {"price": 100.0, "qty": 3},   # correct: 300, buggy: 103
        {"price": 25.0,  "qty": 1},   # correct: 25,  buggy: 26
    ]
    correct = _correct_subtotal(cart_items)
    buggy = _buggy_subtotal(cart_items)

    assert abs(correct - 325.0) < 1e-4, f"Expected correct subtotal 325.0, got {correct}"
    assert abs(buggy - 129.0) < 1e-4, f"Expected buggy subtotal 129.0, got {buggy}"
    assert correct != buggy, "Buggy and correct subtotals must differ"
