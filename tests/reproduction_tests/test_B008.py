"""
Reproduction test for B008.
The stock-overflow check was removed from add_to_cart,
so quantities exceeding available stock are silently accepted.
"""
from fastapi import HTTPException
from app.database import Base
from app.models.product import Product
from app.services import cart_service
from tests.test_utils import engine, TestingSessionLocal


def test_B008():
    """
    Expected: adding quantity=5 to a product with stock=3 raises HTTP 400.
    Actual:   the item is created with quantity=5 despite only 3 in stock.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="B008Prod", category="Cat", price=10.0, stock=3, available=False)
        db.add(p)
        db.commit()
        db.refresh(p)

        try:
            cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=5)
            assert False, "Expected HTTP 400 for quantity exceeding stock but no error was raised"
        except HTTPException as exc:
            assert exc.status_code == 400, f"Expected 400, got {exc.status_code}"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
