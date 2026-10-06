"""
Reproduction test for B018.
cart_service.remove_from_cart filters only by product_id,
dropping the user_id filter:

    BUG:   db.query(CartItem).filter(CartItem.product_id == product_id)
    CORRECT: db.query(CartItem).filter(
                 CartItem.user_id == user_id,
                 CartItem.product_id == product_id
             )

This allows user A to remove an item from user B's cart simply by calling
remove with the same product_id.
"""
from app.database import Base
from app.models.product import Product
from app.services import cart_service
from tests.test_utils import engine, TestingSessionLocal


def test_B018():
    """
    Expected: remove_from_cart(user_id=2, product_id=X) only removes the item
              belonging to user 2; user 1's item with the same product is unaffected.
    Actual:   the first matching product_id across ANY user is deleted — user 1's
              item is removed even though user_id=2 was specified.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        p = Product(name="B018Prod", category="Cat", price=10.0, stock=10, available=False)
        db.add(p)
        db.commit()
        db.refresh(p)

        # Both user 1 and user 2 add the same product
        cart_service.add_to_cart(db, user_id=1, product_id=p.id, quantity=1)
        cart_service.add_to_cart(db, user_id=2, product_id=p.id, quantity=1)

        # User 2 removes from their cart
        cart_service.remove_from_cart(db, user_id=2, product_id=p.id)

        # User 1's cart should be unaffected
        user1_cart = cart_service.get_cart_items(db, user_id=1)
        assert len(user1_cart) == 1, (
            f"User 1's cart should still have 1 item after user 2 removed theirs. "
            f"Got {len(user1_cart)} items — remove_from_cart ignores user_id filter."
        )
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
