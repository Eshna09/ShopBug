"""
Reproduction test for B006.
get_all_products filters Product.available == False instead of == True,
so available products are hidden and unavailable ones are returned.
"""
from app.database import Base
from app.models.product import Product
from app.services import product_service
from tests.test_utils import engine, TestingSessionLocal


def test_B006():
    """
    Expected: list endpoint returns products that are available (stock > 0).
    Actual:   list endpoint returns only products with available=False.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Insert one product with available=True (correct, in-stock product)
        p = Product(name="B006Available", category="Cat", price=10.0, stock=5, available=True)
        db.add(p)
        db.commit()

        results = product_service.get_all_products(db)
        product_names = [r.name for r in results]

        assert "B006Available" in product_names, (
            f"Available product should appear in listing but it is missing. "
            f"Got: {product_names}"
        )
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
