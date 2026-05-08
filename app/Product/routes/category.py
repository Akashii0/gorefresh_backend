from fastapi import APIRouter

from app.Admin.annotations import CurrentAdmin
from app.common.annotations import DatabaseSession
from app.core.settings import get_settings
from app.Product import services
from app.Product.formatters import format_product_category
from app.Product.schemas import create, response

# Globals
router = APIRouter()
settings = get_settings()


@router.post(
    "",
    summary="Create a product Category",
    response_description="The created product category's details",
    status_code=200,
    response_model=response.ProductCategoryResponse,
)
async def route_product_category_create(
    curr_admin: CurrentAdmin,
    category_in: create.ProductCategoryCreate,
    db: DatabaseSession,
):
    """
    This endpoint creates a product category
    """

    # Create the product_category
    product_category = await services.create_product_category(
        data=category_in, admin=curr_admin, db=db
    )

    # Format product category to dict
    return {"data": await format_product_category(product_category=product_category)}
