from sqlalchemy.ext.asyncio import AsyncSession

from app.common.crud import CRUDBase
from app.Order import models


class OrderCRUD(CRUDBase[models.Order]):
    """
    CRUD Class for orders
    """

    def __init__(self, db: AsyncSession):
        super().__init__(models.Order, db)


class OrderItemCRUD(CRUDBase[models.OrderItem]):
    """
    CRUD Class for order items
    """

    def __init__(self, db: AsyncSession):
        super().__init__(models.OrderItem, db)
