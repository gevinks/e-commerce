from app.database.connection import Base
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.sql import func

class Product(Base):
    __tablename__ = "products"
    #primary key
    id = Column(
        Integer,
        index=True,
        autoincrement=True,
        comment="Unique identifier for each product"
    )

    name = Column(
        String,
        index=True,
        nullable=False,
        comment="Name of product"
    )

    price = Column(
        Float,
        nullable=False,
        comment="Price of product"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Description of product"
    )

    stock_quantity = Column(
        Integer,
        nullable=False,
        comment="Stock left"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        comment="If product is available or not"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Time at which product is added"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Time at which product is updated"
    )

    def __repr__(self):
        return f"<Product(id = {self.id}, name = {self.name}, description = {self.description}, price = {self.price}, stock_quantity = {self.stock_quantity}, created_at = {self.created_at}, updated_at = {self.updated_at}, is_active = {self.is_active})"
    
    def __str__(self):
        return self.name
    
    @property
    def is_in_stock(self):
        return self.is_active and self.stock_quantity > 0
    
    def update_stock(self, quantity: int):
        if (quantity < 0):
            raise ValueError("Quantity can't be less than 0")
        self.stock_quantity += quantity

    def soft_delete(self):
        self.is_active = False

    def restore(self):
        self.is_active = True


class Category(Base):
    __tablename__ = "category"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(150),
        nullable=False,
        unique=True,
        index=True
    )

    description = Column(
        Text,
        nullable=True, 
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    is_active = Column(
        Boolean,
        nullable=False
    )

class ProductImage(Base):
    __tablename__ = "product_image"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    product_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    image_url = Column(
        String(150),
        nullable=False
    )

    alt_text = Column(
        String(150),
        nullable=True
    )

    is_primary = Column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    is_active = Column(
        Boolean,
        nullable=False
    )