from pydantic import Field

from app.common.schemas import ResponseSchema
from app.Cart.schemas.base import Cart, CartProduct


class CartProductResponse(ResponseSchema):
    """
    Response schema for cart products
    """

    msg: str = Field(default="cart product retrieved successfully")
    data: CartProduct = Field(description="The details of the cart's product(s)")


class CartResponse(ResponseSchema):
    """
    Response schema for carts
    """

    msg: str = Field(default="cart retrieved successfully")
    data: Cart = Field(description="The details of the cart")
