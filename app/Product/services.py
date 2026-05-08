from datetime import datetime
from typing import cast
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.Admin import models as admin_model
from app.common.exceptions import BadRequest
from app.external.cloudinary.client import ImageService
from app.Product import models, selectors
from app.Product.crud import ProductCategoryCRUD, ProductCRUD, ProductRatingCRUD
from app.Product.schemas import create, edit


async def create_product_category(
    *, data: create.ProductCategoryCreate, admin: admin_model.Admin, db: AsyncSession
):
    """
    Create product category obj

    Args:
        data (create.ProductCategoryCreate): The product category's details
        admin (admin_model.Admin): The admin obj
        db (AsyncSession): The database session

    Returns:
        models.ProductCategory
    """
    # Init product category crud
    product_category_crud = ProductCategoryCRUD(db=db)

    # Check for unique product category name
    if await product_category_crud.get(name=data.name):
        raise BadRequest(f"product category with name: {data.name} already exists")

    # create product category
    product_category = await product_category_crud.create(
        data={"created_by": admin.id, **data.model_dump()}
    )

    return product_category


async def create_product(
    *,
    data: create.ProductCreate,
    admin: admin_model.Admin,
    product_category: models.ProductCategory,
    db: AsyncSession,
):
    """
    Create product obj

    Args:
        data (create.productCreate): The product's details
        admin (admin_model.Admin): The admin obj
        product_category (models.productCategory): The product category obj
        db (AsyncSession): The database session

    Returns:
        models.Product: The created product obj
    """

    # Init product  crud
    product_crud = ProductCRUD(db=db)

    # create product
    product = await product_crud.create(
        data={
            "product_category_id": product_category.id,
            "created_by": admin.id,
            **data.model_dump(),
        }
    )

    return product


async def rate_product(data: create.RatingCreate, product_id: int, db: AsyncSession):
    """
    Rate a product

    Args:
        data (create.RatingCreate): The rating's details
        product_id (int): The ID of the product
        db (AsyncSession): The database session

    Returns:
        models.product: The product obj
    """
    # init CRUD
    rating_crud = ProductRatingCRUD(db=db)
    product = cast(
        models.Product, await selectors.get_product__by_id(id=product_id, db=db)
    )
    await rating_crud.create(data={"product_id": product.id, **data.model_dump()})

    avg, count = await rating_crud.get_ratings(product_id=product_id, db=db)

    setattr(product, "rating", round(avg, 1))
    setattr(product, "no_ratings", count)

    # update the restaurant updated time
    setattr(product, "updated_at", datetime.now())

    await db.commit()

    return product


async def upload_product_thumbnail(
    product_id: int, db: AsyncSession, thumbnail: UploadFile
):
    """
    Upload product image

    Args:
        product_id (int): The ID of the product
        db (AsyncSession): The database session
        thumbnail: product thumbnail image
    """
    # Init Client
    cloudinary = ImageService()

    product = await selectors.get_product_by_id(id=product_id, db=db)

    # Handle thumbnail upload
    thumbnail_url = await cloudinary.upload_image(
        file=thumbnail,
        entity_type="products",
        entity_id=product.id,  # type: ignore
    )
    setattr(product, "thumbnail_url", thumbnail_url)

    # save changes
    await db.commit()

    return thumbnail_url


async def edit_product(
    *,
    data: edit.ProductEdit,
    product: models.Product,
    db: AsyncSession,
):
    """
    Edit product obj

    Args:
        data (create.productEdit): The product's details
        product (models.product): The product item obj
        db (AsyncSession): The database session

    Returns:
        models.product: The edited product item obj
    """
    if data.product_category_id:
        await selectors.get_product_category_by_id(id=data.product_category_id, db=db)

    # Edit product details
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(product, k, v)

    # update the restaurant updated time
    setattr(product, "updated_at", datetime.now())

    # Save changes
    await db.commit()
    await db.refresh(product)

    return product
