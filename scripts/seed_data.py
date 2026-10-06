"""
Seed the ShopBug database with sample products and discount codes.

Run this once after starting the backend (or after the tables have been
created) so the e-commerce frontend has data to display:

    python scripts/seed_data.py

This script inserts products **directly** into the SQLite database using
SQLAlchemy — it does NOT go through the API endpoints, so it bypasses any
business-logic validations in the service layer.  It is idempotent: running
it twice will not create duplicate rows (existing names are skipped).
"""
import sys
import os

# Allow running from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.product import Product
from app.models.order import Discount


SAMPLE_PRODUCTS = [
    # name,              category,      price,   stock
    ("Wireless Mouse",   "Electronics", 29.99,   50),
    ("Mechanical Keyboard", "Electronics", 79.99, 30),
    ("USB-C Hub",        "Electronics", 39.99,   25),
    ("Noise-Cancelling Headphones", "Electronics", 199.99, 15),
    ("Python Programming", "Books",     49.99,   40),
    ("The Clean Coder",  "Books",       34.99,   20),
    ("Cotton T-Shirt",   "Clothing",    19.99,   100),
    ("Denim Jacket",     "Clothing",    89.99,   10),
    ("Yoga Mat",         "Sports",      24.99,   35),
    ("Coffee Maker",     "Home",        99.99,   12),
    ("Desk Lamp",        "Home",        44.99,   28),
    ("Action Figure",    "Toys",        14.99,   60),
]

SAMPLE_DISCOUNTS = [
    # code,         percent,  min_order,  max_discount
    ("SAVE10",      10.0,     0.0,        None),
    ("WELCOME20",   20.0,     100.0,      50.0),
]


def seed():
    """Insert sample products and discounts (idempotent)."""
    db = SessionLocal()
    try:
        # --- Products ---
        for name, category, price, stock in SAMPLE_PRODUCTS:
            existing = db.query(Product).filter(Product.name == name).first()
            if existing:
                continue
            product = Product(
                name=name,
                category=category,
                price=price,
                stock=stock,
                # NOTE: The list endpoint filters by available == False (this is
                # an intentional backend condition).  Setting available=False
                # here ensures products appear in the product list.  The stock
                # field is used by the frontend for display and cart logic.
                available=False,
            )
            db.add(product)

        # --- Discounts ---
        for code, percent, min_order, max_discount in SAMPLE_DISCOUNTS:
            existing = db.query(Discount).filter(Discount.code == code).first()
            if existing:
                continue
            discount = Discount(
                code=code,
                discount_percent=percent,
                min_order_amount=min_order,
                max_discount_amount=max_discount,
            )
            db.add(discount)

        db.commit()

        # Report what is now in the DB
        products = db.query(Product).all()
        discounts = db.query(Discount).all()
        print(f"Seeded {len(products)} product(s) and {len(discounts)} discount(s).")
        for p in products:
            print(f"  Product #{p.id}: {p.name} ({p.category}) - ${p.price} | stock={p.stock} | available={p.available}")
        for d in discounts:
            print(f"  Discount #{d.id}: {d.code} ({d.discount_percent}%) min=${d.min_order_amount} cap={d.max_discount_amount}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
