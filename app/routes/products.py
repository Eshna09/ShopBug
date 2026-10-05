from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.services import product_service

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    return product_service.create_product(db, data)


@router.get("/search", response_model=list[ProductResponse])
def search_products(q: str = Query(...), db: Session = Depends(get_db)):
    return product_service.search_products(db, q)


@router.get("/filter", response_model=list[ProductResponse])
def filter_products(category: str = Query(...), db: Session = Depends(get_db)):
    return product_service.filter_by_category(db, category)


@router.get("/", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return product_service.get_all_products(db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_service.get_product(db, product_id)
