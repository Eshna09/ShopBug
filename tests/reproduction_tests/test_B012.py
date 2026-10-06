"""
Reproduction test for B012.
checkout_service calls cart_service.get_cart_items(db) without the required
user_id argument, causing a TypeError at runtime.
"""
from app.database import Base
from app.models.product import Product
from app.services import cart_service, checkout_service
from tests.test_utils import engine, TestingSessionLocal


def test_B012():
    """
    Expected: checkout retrieves cart items for the correct user and returns an order.
    Actual:   TypeError raised because get_cart_items is called without user_id.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="B012Prod", category="Cat", price=10.0, stock=5, available=False)
        db.add(p)
        db.commit()
        db.refresh(p)

        cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=1)

        raised_type_error = False
        try:
            checkout_service.checkout(db, user_id=1)
        except TypeError as e:
            raised_type_error = True
            assert "user_id" in str(e), (
                f"Expected TypeError about user_id, got: {e}"
            )

        assert raised_type_error, (
            "Expected checkout to raise TypeError because get_cart_items is called "
            "without user_id — B012 may not be active"
        )
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
