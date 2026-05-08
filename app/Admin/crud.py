from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.crud import CRUDBase
from app.Admin import models


class AdminCRUD(CRUDBase[models.Admin]):
    """
    CRUD class for Admins
    """

    def __init__(self, db: AsyncSession):
        super().__init__(models.Admin, db)


class AdminRefreshTokenCRUD(CRUDBase[models.AdminRefreshToken]):
    """
    CRUD class for Admin refresh tokens
    """

    def __init__(self, db: AsyncSession):
        super().__init__(models.AdminRefreshToken, db)

    async def delete_tokens(self, Admin: models.Admin):
        """
        Delete all Admin tokens
        """

        # Delete tokens
        await self.db.execute(delete(self.model).filter_by(Admin_id=Admin.id))
        await self.db.commit()

        return True
