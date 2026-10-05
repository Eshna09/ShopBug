"""Reproduction test for B018 — 100% discount accepted."""
import pytest
from app.database import Base
from app.schemas.order import DiscountCreate
from app.services import discount_service
from tests.test_utils import engine, TestingSessionLocal


def test_B018():
    """Creating a discount with 100% should raise HTTP 400."""
    from fastapi import HTTPException
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        data = DiscountCreate(code="B018TEST", discount_percent=100.0, min_order_amount=0.0)
        try:
            discount_service.create_discount(db, data)
            assert False, "Expected HTTP 400 for 100% discount"
        except HTTPException as exc:
            assert exc.status_code == 400
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
