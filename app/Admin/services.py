# type: ignore
import logging
import secrets
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.Admin import models
from app.Admin.crud import AdminCRUD, AdminRefreshTokenCRUD
from app.Admin.schemas import base, create
from app.common.exceptions import BadRequest, Unauthorized
from app.common.security import hash_password, verify_password
from app.core.settings import get_settings

# Globals
logger = logging.getLogger(__name__)
settings = get_settings()


async def create_first_admin(*, db: AsyncSession):
    """
    Create a new admin if one doesn't exist

    Args:
        data (create.SuperAdminCreate): The admin's details
        db (AsyncSession): The database session

    Returns:
        models.Admin: The created or existing admin object
    """
    logger.info(f"Checking for existing admin with email: {settings.ADMIN_EMAIL}")

    # Init crud
    admin_crud = AdminCRUD(db=db)

    # Check: unique email
    existing_admin = await admin_crud.get(email=settings.ADMIN_EMAIL)
    if existing_admin:
        logger.info("Admin already exists")
        return existing_admin

    # Create new admin if doesn't exist
    hashed_password = await hash_password(raw=settings.ADMIN_PASSWORD)
    admin = models.Admin(
        email=settings.ADMIN_EMAIL,
        first_name=settings.ADMIN_FIRST_NAME,
        last_name=settings.ADMIN_LAST_NAME,
        password=hashed_password,
        phone=settings.ADMIN_PHONE,
        is_active=True,
    )

    db.add(admin)
    await db.commit()
    await db.refresh(admin)

    if admin:
        logger.info("Admin created successfully")
    return admin


async def create_admin(data: create.AdminCreate, db: AsyncSession):
    """
    Create a new admin

    Args:
        data (create.AdminCreate): The admin's details
        db (AsyncSession): The database session

    Raises:
        BadRequest

    Returns:
        models.Admin: The created admin obj
    """
    # Init crud
    admin_crud = AdminCRUD(db=db)

    # Check: unique email
    if await admin_crud.get(email=data.email):
        raise BadRequest("Email already exists")

    # Create admin
    admin = await admin_crud.create(
        data={
            "password": await hash_password(raw=data.password),
            **data.model_dump(exclude={"password"}),
        }
    )
    return admin


async def create_admin_refresh_token(admin: models.Admin, db: AsyncSession):
    """
    Create admin refresh token

    Args:
        admin (models.Admin): The admin obj
        db (AsyncSession): The database session

    Returns:
        models.AdminRefreshToken: The admin refresh token obj
    """
    # Init crud
    ref_token_crud = AdminRefreshTokenCRUD(db=db)

    # Create ref token
    ref_token_obj = await ref_token_crud.create(
        data={
            "admin_id": admin.id,
            "token": secrets.token_hex(),
        }
    )

    return ref_token_obj


async def login_admin(credential: base.AdminLoginCredentials, db: AsyncSession):
    """
    Login admin
    Args:
        credential (base.AdminLoginCredential): The admin's login credentials
        db (Session): The database session

    Raises:
        Unauthorized

    Returns:
        models.Admin
    """
    # Init Crud
    admin_crud = AdminCRUD(db=db)

    # Get admin obj
    obj = await admin_crud.get(email=credential.email)
    if not obj:
        raise Unauthorized("Invalid Login Credentials")

    # Verify password
    if not await verify_password(raw=credential.password, hashed=str(obj.password)):
        raise Unauthorized("Invalid Login Credentials")

    setattr(obj, "last_login", datetime.now())
    await db.commit()

    return obj
