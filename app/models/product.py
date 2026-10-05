from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    available = Column(Boolean, nullable=False, default=True)
