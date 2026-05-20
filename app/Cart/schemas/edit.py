from pydantic import BaseModel, Field


class CartProductEdit(BaseModel):
    """
    Edit schema for cart products
    """

    product_id: int = Field(description="ID of the product editted in the cart")
    quantity: int = Field(description="Quantity of the product")
