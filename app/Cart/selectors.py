from app.core.database import AsyncSession
from app.Cart.crud import CartCRUD, CartProductCRUD
from app.Cart.exceptions import CartProductNotFound, CartNotFound


async def get_cart_by_id(id: int, db: AsyncSession, raise_exc: bool = True):
    """
    Get a cart using it's id

    Args:
        id (int): The ID of the cart
        db (AsyncSession): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        CartNotFound

    Returns:
        models.Cart
    """

    # Init crud
    cart_crud = CartCRUD(db=db)

    # Get cart
    obj = await cart_crud.get(id=id)

    if not obj and raise_exc:
        raise CartNotFound()

    return obj


async def get_cart_by_user_id(user_id: int, db: AsyncSession, raise_exc: bool = True):
    """
    Get a cart using it's user_id

    Args:
        user_id (int): The User ID of the cart
        db (AsyncSession): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        CartNotFound

    Returns:
        models.Cart
    """

    # Init crud
    cart_crud = CartCRUD(db=db)

    # Get cart
    obj = await cart_crud.get(user_id=user_id)

    if not obj and raise_exc:
        raise CartNotFound()

    return obj


async def get_cart_product_by_id(id: int, db: AsyncSession, raise_exc: bool = True):
    """
    Get a cart product using it's id

    Args:
        id (int): The ID of the cart product
        db (AsyncSession): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        CartProductNotFound

    Returns:
        models.CartProduct
    """

    # Init crud
    cart_crud = CartProductCRUD(db=db)

    # Get cart fooditem
    obj = await cart_crud.get(id=id)

    if not obj and raise_exc:
        raise CartProductNotFound()

    return obj
