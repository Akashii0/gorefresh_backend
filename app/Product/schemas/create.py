from typing import Annotated
from pydantic import BaseModel, Field


class ProductCategoryCreate(BaseModel):
    """
    Create schema for product category
    """

    name: str = Field(description="The name of the product category", max_length=250)


class ProductCreate(BaseModel):
    """
    Create schema for product item
    """

    name: str = Field(description="The name of the product")
    description: str = Field(description="The description of the product")
    price: float = Field(description="The price of the product")


class RatingCreate(BaseModel):
    """
    Create schema for product rating
    """

    rating: Annotated[int, Field(ge=1, le=5)]
