from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.order import OrderResponse
from app.services import checkout_service

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=201)
def checkout(user_id: int, discount_id: Optional[int] = None, db: Session = Depends(get_db)):
    return checkout_service.checkout(db, user_id, discount_id)
