from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="ShopBug",
    description="A small e-commerce backend API.",
    version="1.0.0",
    lifespan=lifespan,
)


# Routers will be registered here as modules are implemented
# from app.routes import auth, products, cart, discount, checkout
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(products.router, prefix="/products", tags=["products"])
# app.include_router(cart.router, prefix="/cart", tags=["cart"])
# app.include_router(discount.router, prefix="/discounts", tags=["discounts"])
# app.include_router(checkout.router, prefix="/checkout", tags=["checkout"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
