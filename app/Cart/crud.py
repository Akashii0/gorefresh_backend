from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Cart import models
from app.common.crud import CRUDBase


class CartCRUD(CRUDBase[models.Cart]):
    """
    CRUD Class for carts
    """

    def __init__(self, db: AsyncSession):
        super().__init__(models.Cart, db)

    async def delete_by_cart(self, cart_id: int):
        await self.db.execute(delete(self.model).where(self.model.id == cart_id))
        return True

    async def clear_cart_items(self, cart: models.Cart):
        await self.db.execute(
            delete(models.CartProduct).where(models.CartProduct.cart_id == cart.id)
        )
        return True

    async def delete_cart(self, cart: models.Cart):
        """
        Deletes a cart
        """
        await self.db.delete(cart)
        await self.db.commit()

        return True


class CartProductCRUD(CRUDBase[models.CartProduct]):
    """
    CRUD Class for Cart products
    """

    def __init__(self, db: AsyncSession):
        super().__init__(models.CartProduct, db)

    async def get_by_cart_and_product(self, cart_id: int, product_id: int):
        result = await self.db.execute(
            select(self.model)
            .where(self.model.cart_id == cart_id)
            .where(self.model.product_id == product_id)
        )
        return result.scalars().first()

    async def get_by_cart_id(self, cart_id: int) -> list[models.CartProduct]:
        result = await self.db.execute(
            select(self.model).where(self.model.cart_id == cart_id)
        )
        return list(result.scalars().all())

    async def bulk_create(self, items: list[dict], commit: bool = True):
        await self.db.execute(insert(self.model).values(items))
        if commit:
            await self.db.commit()

    async def delete(self, product: models.CartProduct):
        await self.db.delete(product)
        await self.db.commit()
        return True
