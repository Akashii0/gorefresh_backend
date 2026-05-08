from app.core.database import AsyncSession
from app.Product.crud import ProductCategoryCRUD, ProductCRUD
from app.Product.exceptions import ProductCategoryNotFound, ProductNotFound


async def get_product_category_by_id(id: int, db: AsyncSession, raise_exc: bool = True):
    """
    Get a product category using it's id

    Args:
        id (int): The ID of the product category
        db (AsyncSession): The database session
        raise_exc (bool = True): raise a 404 if not found`

    Raises:
        productCategorytNotFound

    Returns:
        models.productCategory | None
    """

    # Init crud
    product_category_crud = ProductCategoryCRUD(db=db)

    # Get product category
    obj = await product_category_crud.get(id=id)

    if not obj and raise_exc:
        raise ProductCategoryNotFound()

    return obj


async def get_product_by_id(id: int, db: AsyncSession, raise_exc: bool = True):
    """
    Get a product item using it's id

    Args:
        id (int): The ID of the product item
        db (AsyncSession): The database session
        raise_exc (bool = True): raise a 404 if not found`

    Raises:
        productNotFound

    Returns:
        models.product | None
    """

    # Init crud
    product_crud = ProductCRUD(db=db)

    # Get product item
    obj = await product_crud.get(id=id)

    if not obj and raise_exc:
        raise ProductNotFound()

    return obj
