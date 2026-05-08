from fastapi import APIRouter

from app.core.tags import RouteTags
from app.Product.routes.base import router as base_router
from app.Product.routes.category import router as category_router
from app.Product.routes.image import router as image_router

# Globals
router = APIRouter()
tags = RouteTags()

# Routes
router.include_router(base_router, prefix="/products")
router.include_router(
    category_router, prefix="/products/categories", tags=[tags.PRODUCT_CATEGORY]
)
router.include_router(image_router, prefix="/products/images", tags=[tags.PRODUCT_IMAGE])
