from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class CartProduct(BaseModel):
    """
    Base schema for cart products
    """

    id: int = Field(description="The cart product's ID")
    cart_id: int = Field(description="ID of the cart the product belongs to")
    product_id: int = Field(description="ID of the product added to the cart")
    product_thumbnail: str = Field(description="The thumbnail url of the fooditem")
    product_name: str = Field(description="The name of the product added to cart")
    product_category: str = Field(
        description="The category of the product added to cart"
    )
    quantity: int = Field(description="Quantity of the product")
    unit_price: int = Field(gt=0, description="The individual price of the product")


class Cart(BaseModel):
    """
    Base schema for carts
    """

    id: int = Field(description="The ID of the cart")
    user_id: int = Field(description="ID of the user the cart belongs to")
    delivery_fee: int = Field(description="The delivery fee to be charged")
    subtotal: float = Field(description="The cart's subtotal")
    service_fee: float = Field(description="The service fee to be charged")
    total_amount: float = Field(description="The total cart item Price")
    updated_at: datetime | None = Field(description="The updated time")
    created_at: datetime = Field(description="The time the cart was created")

    products: List[CartProduct] = Field(
        default_factory=list, description="List of products in the cart"
    )
