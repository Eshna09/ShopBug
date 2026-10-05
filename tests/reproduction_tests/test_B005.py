"""Reproduction test for B005 — negative price accepted."""
import pytest
from app.database import Base
from app.schemas.product import ProductCreate
from app.services import product_service
from tests.test_utils import engine, TestingSessionLocal


def test_B005():
    """Creating product with negative price should raise HTTP 400."""
    from fastapi import HTTPException
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        data = ProductCreate(name="B005Prod", category="Cat", price=-10.0, stock=1)
        try:
            product_service.create_product(db, data)
            assert False, "Expected HTTP 400 for negative price"
        except HTTPException as exc:
            assert exc.status_code == 400
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
