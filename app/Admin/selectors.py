from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.annotations import DatabaseSession
from app.common.exceptions import Forbidden, Unauthorized
from app.core.settings import get_settings
from app.Admin.auth import AdminTokenGenerator
from app.Admin.crud import AdminCRUD, AdminRefreshTokenCRUD
from app.Admin.exceptions import AdminNotFound

# Globals
settings = get_settings()
token_gen = AdminTokenGenerator()


async def get_admin_by_id(
    id: int, db: AsyncSession, raise_exc: bool = True, return_active: bool = True
):
    """
    Get Admin obj based on the Admin's ID

    Args:
        id (int): The Admin's id
        db (AsyncSession): The database Session
        raise_exc (bool): Raises a 404 error if the Admin is not found. Defaults to True.
        return_disabled (bool = False)

    Raises:
        AdminNotFound

    Returns:
        models.Admin: The Admin object
    """
    # init CRUD
    admin_crud = AdminCRUD(db=db)

    # get Admin by id
    admin = await admin_crud.get(id=id)

    # Check: Admin not found
    if not admin and raise_exc:
        raise AdminNotFound()

    # Check: inactive Admin
    if admin and not bool(admin.is_active) and return_active:
        raise Forbidden("Admin has been deactivated")

    return admin


async def get_current_admin(
    token: Annotated[str | None, Header(alias="Authorization")],
    db: DatabaseSession,
):
    """
    Returns Current Admin logged in

    Args:
        token (str): Authorization token.
        db (AsyncSession): The database session

    Raises:
        Unauthorized: Invalid Token
        ValueError: Admin ID cannot be None

    Returns:
        models.Admin: The Admin object
    """
    # Check: header exists
    if not token:
        raise Unauthorized("Authorization header missing")

    # Validate format: Bearer <token>
    parts = token.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise Unauthorized("Invalid authorization header format")

    token = parts[1]

    # Verify token
    admin_id = await token_gen.verify(token=token, sub_head="ADMIN", db=db)

    admin = await get_admin_by_id(id=int(admin_id), db=db)

    return admin


#####################################################################
# ADMIN REFRESH TOKEN
#####################################################################
async def get_admin_refresh_token(token: str, db: AsyncSession):
    """
    Get Admin refresh token

    Args:
        token (str): The refresh
        db (AsyncSession): The database session

    Raises:
        Unauthorized: Refresh token not found
        Unauthorized: Refresh token has expired

    Returns:
        models.AdminRefreshToken: The Admin's refresh token
    """
    # Init crud
    ref_token_crud = AdminRefreshTokenCRUD(db=db)

    # Get ref token
    ref_token = await ref_token_crud.get(token=token)

    # Check: exists
    if not ref_token:
        raise Unauthorized("Refresh token not found")

    # Check: expired
    token_expires_at: datetime = ref_token.created_at + timedelta(
        hours=settings.REFRESH_TOKEN_EXPIRE_HOUR  # type: ignore
    )
    if datetime.now() > token_expires_at.replace(tzinfo=None):
        raise Unauthorized("Refresh token has expired")

    return ref_token
