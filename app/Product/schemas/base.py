from datetime import datetime

from pydantic import BaseModel, Field

from app.core.settings import get_settings
from app.Admin.schemas import base as admin_base

# Globals
settings = get_settings()


class ProductCategory(BaseModel):
    """
    Base schema for product categories
    """

    id: int = Field(description="The product category's id")
    thumbnail_url: str = Field(
        description="The url of the product category's thumbnail"
    )
    name: str = Field(description="The name of the product category")
    updated_at: datetime | None = Field(description="The time it was updated")
    created_at: datetime = Field(description="The time it was updated was created")
    created_by: admin_base.AdminSummary = Field(description="The Admin's summary data")


class ProductCategorySummary(BaseModel):
    """
    Base schema for product categories summary
    """

    id: int = Field(description="The product category's id")
    thumbnail_url: str = Field(
        description="The url of the product category's thumbnail"
    )
    name: str = Field(description="The name of the product category")


class Product(BaseModel):
    """
    Base schema for products
    """

    id: int = Field(description="The product item's id")
    name: str = Field(description="The name of the product item")
    description: str = Field(description="The description of the product item")
    thumbnail_url: str = Field(description="The url of the product item's thumbnail")
    price: float = Field(description="The price of the product item")
    rating: float = Field(description="The rating of the product item")
    is_available: bool = Field(description="Indicates if the product item is available")
    no_orders: int = Field(
        description="The number of orders that have been placed for the product item"
    )
    no_ratings: int = Field(
        description="The number of ratings the product item has received"
    )
    updated_at: datetime | None = Field(description="The time it was updated")
    created_at: datetime = Field(description="The time it was updated was created")
    product_category: ProductCategory = Field(
        description="The product category details"
    )
    created_by: admin_base.AdminSummary | None = Field(
        description="The Admin's summary data"
    )


class ProductSummary(BaseModel):
    """
    Base schema for product's summary
    """

    id: int = Field(description="The product item's id")
    thumbnail_url: str = Field(description="The url of the product item's thumbnail")
    name: str = Field(description="The name of the product item")
    description: str = Field(description="The description of the product item")
    price: float = Field(description="The price of the product item")
    product_category: ProductCategorySummary = Field(
        description="The product category summary details"
    )
    rating: float = Field(description="The rating of the product item")
