from pydantic import BaseModel
from app.schemas.product import ProductResponse


class CartItemCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class CartItemUpdate(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product: ProductResponse
    model_config = {"from_attributes": True}
