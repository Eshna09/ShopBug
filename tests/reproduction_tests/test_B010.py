"""
Reproduction test for B010.
The empty-cart guard in checkout_service uses `if items:` (truthy = non-empty)
and raises 400, which is the inverse of the intended behaviour.

Note: B012 (missing user_id in get_cart_items) causes a TypeError before
the guard is ever evaluated.  This test verifies the guard logic directly
by patching around the missing-user_id issue, isolating B010 alone.
"""
import app.services.checkout_service as checkout_mod
import app.services.cart_service as cart_mod
from fastapi import HTTPException
from app.database import Base
from app.models.product import Product
from app.services import cart_service
from tests.test_utils import engine, TestingSessionLocal


def test_B010():
    """
    Expected: checkout with items in cart succeeds (HTTP 200/order returned).
    Actual:   the guard `if items:` raises HTTP 400 on a non-empty cart.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="B010Prod", category="Cat", price=10.0, stock=5, available=False)
        db.add(p)
        db.commit()
        db.refresh(p)
        cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=1)

        # Patch get_cart_items to fix B012 so B010 can be isolated
        original_get = cart_mod.get_cart_items
        def fixed_get(db_arg, user_id=None):
            if user_id is None:
                user_id = 1
            return original_get(db_arg, user_id)
        cart_mod.get_cart_items = fixed_get

        try:
            try:
                order = checkout_mod.checkout(db, user_id=1)
                # If checkout succeeds, that would be correct — but then bug is not active
                assert order is not None, "Expected checkout to return an order"
            except HTTPException as exc:
                assert exc.status_code != 400 or "empty" not in str(exc.detail).lower(), (
                    f"Non-empty cart was rejected — inverted guard is active (B010): {exc.detail}"
                )
                # Re-raise so the test fails with the right message
                raise AssertionError(
                    f"Checkout raised HTTP {exc.status_code}: '{exc.detail}' — "
                    f"the inverted guard `if items:` rejects non-empty carts (B010 is active)"
                )
        finally:
            cart_mod.get_cart_items = original_get
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
