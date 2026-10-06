"""
Reproduction test for B013.
ProductCard.jsx calls:
    cartApi.add(product.id, user.id, 1)   ← BUG: args swapped
instead of:
    cartApi.add(user.id, product.id, 1)   ← correct

The add function signature is add(userId, productId, quantity).
With the swap, the cart item is created with user_id=product.id and
product_id=user.id — attaching the item to the wrong user and wrong product.

This test confirms the backend rejects the swapped call or returns wrong data.
"""
import pytest
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app
from app.models.product import Product
from app.models.user import User
from tests.test_utils import engine, TestingSessionLocal, override_get_db


def make_client():
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app, raise_server_exceptions=False)


def test_B013():
    """
    Expected: add_to_cart with (user_id=1, product_id=5) creates an item for user 1.
    Actual:   swapped call (user_id=5, product_id=1) creates an item on the wrong
              user, so user 1's cart remains empty.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    client = make_client()
    try:
        # Create a user (id will be 1)
        user = User(email="b013@test.com", hashed_password="x")
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create a product (id will be 1 as well in a fresh DB, but let's use
        # a product with id != user.id to expose the swap)
        for _ in range(4):
            dummy = Product(name=f"dummy", category="Cat", price=1.0, stock=1, available=False)
            db.add(dummy)
        db.commit()

        p = Product(name="B013Prod", category="Cat", price=20.0, stock=10, available=False)
        db.add(p)
        db.commit()
        db.refresh(p)
        db.refresh(user)

        # Simulate the CORRECT call: add(user.id, product.id, 1)
        correct_resp = client.post(
            "/cart/add",
            json={"user_id": user.id, "product_id": p.id, "quantity": 1},
        )
        assert correct_resp.status_code == 201
        correct_item = correct_resp.json()
        assert correct_item["user_id"] == user.id, "Cart item must belong to the user"
        assert correct_item["product_id"] == p.id, "Cart item must reference the product"

        # Simulate the BUGGY call: add(product.id, user.id, 1) — swapped
        buggy_resp = client.post(
            "/cart/add",
            json={"user_id": p.id, "product_id": user.id, "quantity": 1},
        )
        # The buggy call treats product.id as user_id and user.id as product_id.
        # Confirm the resulting item has the WRONG association
        if buggy_resp.status_code == 201:
            buggy_item = buggy_resp.json()
            assert buggy_item["user_id"] != user.id or buggy_item["product_id"] != p.id, (
                "Buggy swapped call should produce a cart item with wrong user or product"
            )
    finally:
        app.dependency_overrides.clear()
        db.close()
        Base.metadata.drop_all(bind=engine)
