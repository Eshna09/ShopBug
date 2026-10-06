from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product import Product
from app.schemas.product import ProductCreate


def create_product(db: Session, data: ProductCreate) -> Product:
    if data.price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than zero.")
    if data.stock < 0:
        raise HTTPException(status_code=400, detail="Stock cannot be negative.")
    product = Product(
        name=data.name,
        category=data.category,
        price=data.price,
        stock=data.stock,
        available=data.stock > 0,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found.")
    return product


def get_all_products(db: Session) -> list[Product]:
    return db.query(Product).filter(Product.available == False).all()


def search_products(db: Session, query: str) -> list[Product]:
    return db.query(Product).filter(Product.name.ilike(f"%{query}%")).all()


def filter_by_category(db: Session, category: str) -> list[Product]:
    return db.query(Product).filter(Product.category == category).all()
