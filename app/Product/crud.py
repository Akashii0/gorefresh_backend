from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.crud import CRUDBase
from app.Product import models


class ProductCategoryCRUD(CRUDBase[models.ProductCategory]):
    """
    CRUD Class for product categories
    """

    def __init__(self, db: AsyncSession):
        super().__init__(models.ProductCategory, db)

    async def get_with_pagination(
        self, *, page: int, size: int, search_name: str | None = None
    ):
        offset = (page - 1) * size
        query = select(self.model)

        if search_name:
            query = query.where(models.ProductCategory.name.ilike(f"%{search_name}%"))

        result = await self.db.execute(query.offset(offset).limit(size))
        categories = result.scalars().all()

        count_query = select(func.count()).select_from(self.model)
        if search_name:
            count_query = count_query.where(
                models.ProductCategory.name.ilike(f"%{search_name}%")
            )

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        return categories, total


class ProductCRUD(CRUDBase[models.Product]):
    """
    CRUD Class for product items
    """

    def __init__(self, db: AsyncSession):
        super().__init__(models.Product, db)

    async def get_with_pagination(
        self,
        *,
        page: int = 1,
        size: int = 10,
        category_id: int | None = None,
        search_name: str | None = None,
    ):
        offset = (page - 1) * size

        # Fetch all Products
        query = select(self.model)
        if category_id:
            query = query.where(models.Product.product_category_id == category_id)
        if search_name:
            query = query.where(models.Product.name.ilike(f"%{search_name}%"))

        result = await self.db.execute(query.offset(offset).limit(size))
        Products = result.scalars().all()

        # Total count (with same filter)
        count_query = select(func.count()).select_from(self.model)
        if category_id:
            count_query = count_query.where(
                models.Product.product_category_id == category_id
            )
        if search_name:
            count_query = count_query.where(
                models.Product.name.ilike(f"%{search_name}%")
            )

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        return Products, total


class ProductRatingCRUD(CRUDBase[models.ProductRating]):
    """
    CRUD Class for Product ratings
    """

    def __init__(self, db: AsyncSession):
        super().__init__(models.ProductRating, db)

    async def get_ratings(self, product_id: int, db: AsyncSession):
        result = await db.execute(
            select(func.avg(models.ProductRating.rating), func.count()).where(
                models.ProductRating.product_item_id == product_id
            )
        )
        avg, count = result.one()

        return avg, count
