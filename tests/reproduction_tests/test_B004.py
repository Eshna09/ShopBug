"""
Reproduction test for B004.
add_to_cart uses quantity < 0 instead of quantity <= 0,
so a zero-quantity item is accepted without error.
"""
from fastapi import HTTPException
from app.database import Base
from app.models.product import Product
from app.services import cart_service
from tests.test_utils import engine, TestingSessionLocal


def test_B004():
    """
    Expected: adding a product with quantity=0 raises HTTP 400.
    Actual:   the item is created with quantity=0, no error raised.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="B004Prod", category="Cat", price=10.0, stock=5, available=False)
        db.add(p)
        db.commit()
        db.refresh(p)

        try:
            cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=0)
            assert False, "Expected HTTP 400 for quantity=0 but no exception was raised"
        except HTTPException as exc:
            assert exc.status_code == 400, f"Expected 400, got {exc.status_code}"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
