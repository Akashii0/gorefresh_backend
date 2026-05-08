from pydantic import BaseModel, Field


class ProductEdit(BaseModel):
    """
    Edit schema for products
    """

    name: str | None = Field(default=None, description="The name of the product")
    description: str | None = Field(
        default=None, description="The description of the product"
    )
    price: float | None = Field(default=None, description="The price of the product")
    product_category_id: int | None = Field(
        default=None, description="The edited product category ID"
    )
