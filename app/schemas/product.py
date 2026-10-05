from pydantic import BaseModel
from typing import Optional


class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    stock: int = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock: int
    available: bool
    model_config = {"from_attributes": True}
