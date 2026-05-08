from pydantic import Field

from app.common.schemas import ResponseSchema
from app.Product.schemas.base import (
    ProductCategory,
    ProductCategorySummary,
    Product,
    ProductSummary,
)


class ProductCategoryResponse(ResponseSchema):
    """
    Response schema for product categories
    """

    msg: str = Field(default="product's category retrieved successfully")
    data: ProductCategory = Field(description="The details of the product category")


class ProductCategoryListResponse(ResponseSchema):
    """
    Response schema for list of product categories
    """

    msg: str = Field(default="List of product categories retrieved successfully")
    data: list[ProductCategorySummary] = Field(
        description="The details of the product category"
    )


class ProductResponse(ResponseSchema):
    """
    Response schema for productitems
    """

    msg: str = Field(default="productItem retrieved succesfully")
    data: Product = Field(description="The details of the product item")


class ProductListResponse(ResponseSchema):
    """
    Response schema for list of productitems
    """

    msg: str = Field(default="List of productItem retrieved succesfully")
    data: list[ProductSummary] = Field(description="The list of product items")
    meta: dict = Field(description="The metadata of the paginated response")
