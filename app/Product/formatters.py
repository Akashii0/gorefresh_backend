from app.Product import models
from app.Admin import formatters as admin_formatters


async def format_product_category(product_category: models.ProductCategory):
    """
    Formats product category obj to dict
    """
    return {
        "id": product_category.id,
        "thumbnail_url": product_category.thumbnail_url,
        "name": product_category.name,
        "updated_at": product_category.updated_at,
        "created_at": product_category.created_at,
        "created_by": await admin_formatters.format_admin_summary(
            admin=product_category.admin
        ),
    }


async def format_product_category_summary(product_category: models.ProductCategory):
    """
    Formats product category obj to dict
    """
    return {
        "id": product_category.id,
        "thumbnail_url": product_category.thumbnail_url,
        "name": product_category.name,
    }


async def format_product(product: models.Product):
    """
    Formats product to dict
    """

    return {
        "id": product.id,
        "thumbnail_url": product.thumbnail_url,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "product_category": await format_product_category(
            product_category=product.category
        ),
        "rating": product.rating,
        "is_available": product.is_available,
        "no_orders": product.no_orders,
        "no_ratings": product.no_ratings,
        "updated_at": product.updated_at,
        "created_at": product.created_at,
        "created_by": await admin_formatters.format_admin_summary(
            admin=product.admin
        )
        if product.created_by  # type: ignore
        else None,
    }


async def format_product_summary(product: models.Product):
    """
    Formats product item to dict
    """

    return {
        "id": product.id,
        "thumbnail_url": product.thumbnail_url,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "product_category": await format_product_category_summary(
            product_category=product.category
        ),
        "rating": product.rating,
    }
