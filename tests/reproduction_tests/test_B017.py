"""
Reproduction test for B017.
get_cart_subtotal multiplies item.product.stock by item.quantity
instead of item.product.price by item.quantity.
"""
from app.database import Base
from app.models.product import Product
from app.services import cart_service
from tests.test_utils import engine, TestingSessionLocal


def test_B017():
    """
    Expected: product price=$100, stock=5, quantity=2 → subtotal = 100*2 = $200.
    Actual:   subtotal uses stock instead of price → 5*2 = $10.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="B017Prod", category="Cat", price=100.0, stock=5, available=False)
        db.add(p)
        db.commit()
        db.refresh(p)

        cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=2)
        subtotal = cart_service.get_cart_subtotal(db, user_id=1)

        assert abs(subtotal - 200.0) < 1e-4, (
            f"Expected subtotal=200.0 (price*qty), got {subtotal} — "
            f"looks like stock ({p.stock}) was used instead of price ({p.price})"
        )
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
