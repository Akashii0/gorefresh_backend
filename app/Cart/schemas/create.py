from typing import List

from pydantic import BaseModel, Field


class CartProductCreate(BaseModel):
    """
    Create schema for cart product
    """

    product_id: int = Field(description="ID of the product added to the cart")
    quantity: int = Field(description="Quantity of the product")


class CartProductBulkCreate(BaseModel):
    """
    Create schema for bulk cart product
    """

    products: List[CartProductCreate] = Field(
        default=None, description="list of products in the cart"
    )


class CartCreate(BaseModel):
    """
    Create schema for carts
    """

    products: List[CartProductCreate] = Field(
        min_length=1,
        description="Optional list of products in the cart",
    )
