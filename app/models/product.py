from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    name:str = Field(..., min_length=3, max_length=100, description="Name of the product")
    price:float = Field(..., gt=0, le=100000, description="Price of product")
    stock_quantity:int = Field(..., gt=0, le=10000, description="Stocks left")
    description:Optional[str] = Field(None, max_length=500, description="Description of product")

    @field_validator("name")
    def validate_product_name(cls, v: str):
        v = v.strip()
        reserved_names = ["admin", "test", "demo", "null", "undefined", "system"]
        inappropriate_words = ["spam", "fake", "scam"]

        if v.lower() in reserved_names:
            raise ValueError(f"Product name {v} is invalid")
        
        if v.lower() in inappropriate_words:
            raise ValueError(f"Product name {v} is inappropriate")
        
        return v
    
    @field_validator("price")
    def validate_product_price(cls, v:float):
        v = round(v, 2)

        if (v < 0.1):
            raise ValueError("Product price {v} should be greater than 0.1 INR")
        
        if (v > 100000):
            raise ValueError(f"Product price {v} should be less than 100000")
        
        return v
    
class ProductResponse(ProductBase):
    id:int = Field(..., description="Id of product")
    is_active:bool = Field(True, description="If the product is for sale now.")
    created_at:Optional[datetime] = Field(None, description="Created time")
    updated_at:Optional[datetime] = Field(None, description="Updated time")

    @property
    def display_price(self) -> str:
        return f"{self.price:,.2f}"
    
    @property
    def is_in_stock(self) -> bool:
        return self.is_active and self.stock_quantity > 0
    
    class Config:
        from_attributes = True

class ProductCreate(ProductBase):

    @field_validator
    def validate_stock_quantity(cls, value: str):
        if value is None:
            return 0
        if (value < 0):
            raise ValueError(f"Stock quantity cannot be negative")
        if (value > 99999):
            raise ValueError(f"Quantity cannot exceed 99999")
        return value
    
class ProductUpdate(BaseModel):
    name:Optional[str] = Field(None, min_length=3, max_length=100, description="Name of the product")
    price:Optional[float] = Field(None, gt=0, le=100000, description="Price of product")
    stock_quantity:Optional[int] = Field(None, gt=0, le=10000, description="Stocks left")
    description:Optional[str] = Field(None, max_length=500, description="Description of product")

    @field_validator
    def validate_product_name(cls, v):
        if v is not None:
            return ProductBase.validate_product_name(v)
        return v
    
    @field_validator
    def validate_product_price(cls, v):
        if (v is not None):
            return ProductBase.validate_product_price(v)
        return v
    
    class Config:
        from_attributes = True
        extra = "forbid"

class ProductSearchFilter(BaseModel):
    active_only: Optional[bool] = Field(True, description="If active")
    min_price: Optional[float] = Field(None, gt=0, le=100000, description="min price")
    max_price: Optional[float] = Field(None, gt=0, le=100000, description="max price")
    name_contains: Optional[str] = Field(None, min_length=3, max_length=100, description="Name filter")
    sort_by:Optional[str] = Field(default="created_at", description="Sort by Value")
    sort_order: Optional[str] = Field(default="desc", regex="^(asc|desc)$", description="sort order")

class ProductListResponse(BaseModel):
    products:List[ProductResponse] = Field(..., description="products list")
    total_count: int = Field(..., description="Total products")
    page: int = Field(..., description="current page")
    page_size: int = Field(..., description="number of products in page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="If next page is there")
    has_previous: bool = Field(..., description="If previous page is there")