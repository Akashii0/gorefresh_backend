from typing import cast
from fastapi import APIRouter, Query

from app.common.annotations import DatabaseSession
from app.Admin.annotations import CurrentAdmin
from app.common.paginators import get_pagination_metadata
from app.core.settings import get_settings
from app.Product import models, selectors, services
from app.Product.crud import ProductCategoryCRUD, ProductCRUD
from app.Product.formatters import (
    format_product_category_summary,
    format_product,
    format_product_summary,
)
from app.Product.schemas import create, edit, response

# Globals
router = APIRouter()
settings = get_settings()


@router.post(
    "",
    summary="Create a product",
    response_description="The created product",
    status_code=200,
    response_model=response.ProductResponse,
)
async def route_product_create(
    curr_admin: CurrentAdmin,
    product_category_id: int,
    product_in: create.ProductCreate,
    db: DatabaseSession,
):
    """
    This endpoint creates a product
    """

    # check for the product category
    product_category = await selectors.get_product_category_by_id(
        id=product_category_id, db=db
    )

    # create the product
    product = await services.create_product(
        data=product_in,
        admin=curr_admin,
        product_category=product_category,
        db=db,
    )

    # Format product  to dict
    return {"data": await format_product(product=product)}


@router.get(
    "/categories",
    summary="Get all product categories",
    response_description="List of all product categories",
    status_code=200,
    response_model=response.ProductCategoryListResponse,
)
async def route_fetch_all_product_categories(
    db: DatabaseSession,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search_name: str | None = Query(None, description="Search by category name"),
):
    """
    Get all product categories with pagination, optionally filtered by search_name
    """
    category_crud = ProductCategoryCRUD(db)
    categories, total = await category_crud.get_with_pagination(
        page=page,
        size=size,
        search_name=search_name,
    )

    total = cast(int, total)
    meta = get_pagination_metadata(
        tno_s=int(total),
        count=len(categories),
        page=page,
        size=size,
    )

    return {
        "data": [
            await format_product_category_summary(category) for category in categories
        ],
        "meta": meta,
    }


@router.get(
    "/{product_id}",
    summary="Get product information",
    response_description="The product's information",
    status_code=200,
    response_model=response.ProductResponse,
)
async def route_restaurant_info(product_id: int, db: DatabaseSession):
    """
    This endpoint returns the product's information
    """

    # Get product
    product = cast(
        models.Product, await selectors.get_product_by_id(id=product_id, db=db)
    )

    return {"data": await format_product(product=product)}


@router.get(
    "",
    summary="Get all product's information",
    response_description="List of all product's",
    status_code=200,
    response_model=response.ProductListResponse,
)
async def route_fetch_all_products(
    db: DatabaseSession,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    category_id: int | None = Query(None, description="Filter by product category ID"),
    search_name: str | None = Query(None, description="Search by product name"),
):
    """
    Get all products with pagination, optionally filtered by category
    """
    product_crud = ProductCRUD(db)
    products, total = await product_crud.get_with_pagination(
        page=page,
        size=size,
        category_id=category_id,
        search_name=search_name,
    )

    total = cast(int, total)
    meta = get_pagination_metadata(
        tno_items=int(total),
        count=len(products),
        page=page,
        size=size,
    )

    return {
        "data": [await format_product_summary(product) for product in products],
        "meta": meta,
    }


@router.post(
    "/{product_id}/rate",
    summary="Rate a product",
    response_description="The product was rated successfully",
    status_code=200,
    response_model=response.ProductResponse,
)
async def route_rate_restaurant(
    product_id: int, rating_in: create.RatingCreate, db: DatabaseSession
):
    """
    This endpoint rates a restaurant
    """

    product_rating = await services.rate_product(
        data=rating_in, product_id=product_id, db=db
    )

    return {"data": await format_product(product_=product_rating)}


@router.put(
    "/{product_id}",
    summary="Edit a product ",
    response_description="The Edited product",
    status_code=200,
    response_model=response.ProductResponse,
)
async def route_product_edit(
    curr_admin: CurrentAdmin,
    product_id: int,
    product_in: edit.ProductEdit,
    db: DatabaseSession,
):
    """
    This endpoint creates a product
    """

    # check for the restaurant
    product = await selectors.get_product_by_id(id=product_id, db=db)

    # create the product
    product = await services.edit_product(
        data=product_in,
        product=product,
        db=db,
    )

    # Format product to dict
    return {"data": await format_product(product_=product)}
