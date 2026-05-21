from app.core.database import AsyncSession
from app.Order.crud import OrderCRUD, OrderItemCRUD
from app.Order.exceptions import OrderItemNotFound, OrderNotFound


async def get_order_by_id(id: int, db: AsyncSession, raise_exc: bool = True):
    """
    Get an order using it's id

    Args:
        id (int): The ID of the order
        db (AsyncSession): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        OrderNotFound

    Returns:
        models.Order
    """

    # Init crud
    order_crud = OrderCRUD(db=db)

    # Get order
    obj = await order_crud.get(id=id)

    if not obj and raise_exc:
        raise OrderNotFound()

    return obj


async def get_order_by_ref(id: str, db: AsyncSession, raise_exc: bool = True):
    """
    Get an order using it's payment reference

    Args:
        id (str): The ID of the payment reference
        db (AsyncSession): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        OrderNotFound

    Returns:
        models.Order
    """

    # Init crud
    order_crud = OrderCRUD(db=db)

    # Get order payment reference
    obj = await order_crud.get(paystack_reference=id)

    if not obj and raise_exc:
        raise OrderNotFound()

    return obj


async def get_order_item_by_id(id: int, db: AsyncSession, raise_exc: bool = True):
    """
    Get an order item using it's id

    Args:
        id (int): The ID of the order item
        db (AsyncSession): The database session
        raise_exc (bool = True): raise a 404 if not found

    Raises:
        OrderItemNotFound

    Returns:
        models.OrderItem
    """

    # Init crud
    order_crud = OrderItemCRUD(db=db)

    # Get order item
    obj = await order_crud.get(id=id)

    if not obj and raise_exc:
        raise OrderItemNotFound()

    return obj
