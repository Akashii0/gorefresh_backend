from typing import Annotated

from fastapi import APIRouter, Body

from app.common.annotations import DatabaseSession
from app.common.schemas import ResponseSchema
from app.core.settings import get_settings
from app.Admin import selectors, services
from app.Admin.annotations import CurrentAdmin
from app.Admin.crud import AdminRefreshTokenCRUD
from app.Admin.schemas import base, create, response
from app.Admin import formatters
from app.Admin.auth import AdminTokenGenerator


# Globals
router = APIRouter()
settings = get_settings()
token_generator = AdminTokenGenerator()


#####################################################################
# BASE
#####################################################################
@router.post(
    "",
    summary="Create a new admin",
    response_description="The created admin's data",
    status_code=200,
    response_model=response.AdminResponse,
)
async def route_create_admin(admin_in: create.AdminCreate, db: DatabaseSession):
    """
    This endpoint creates a admin
    """

    # Create the admin
    admin = await services.create_admin(data=admin_in, db=db)

    return {"data": await formatters.format_admin(admin)}


#####################################################################
# AUTH
#####################################################################
@router.post(
    "/login",
    summary="Login admin",
    response_description="The admin's access token",
    status_code=200,
    response_model=response.AdminLoginResponse,
)
async def route_admin_login(cred_in: base.AdminLoginCredentials, db: DatabaseSession):
    """
    This endpoint logs in a admin
    """

    # Login admin
    admin = await services.login_admin(credential=cred_in, db=db)

    # Generate refresh token
    ref_token = await services.create_admin_refresh_token(admin=admin, db=db)

    # Generate access token
    access_token = await token_generator.generate(
        sub=f"ADMIN-{admin.id}",
        ref_id=ref_token.id,  # type: ignore
    )

    await db.commit()

    return {
        "data": {
            "admin": await formatters.format_admin(admin),
            "tokens": {"access_token": access_token, "refresh_token": ref_token.token},
        }
    }


@router.post(
    "/token",
    summary="Refresh admin Token",
    response_description="The new admin token",
    status_code=200,
    response_model=response.AdminLoginResponse,
)
async def route_admin_token(
    token: Annotated[str, Body(embed=True, description="The admin's token")],
    db: DatabaseSession,
):
    """
    This endpoint refreshes the admin's token
    """

    # Verify refresh token
    ref_token = await selectors.get_admin_refresh_token(token=token, db=db)

    # Generate access token
    access_token = await token_generator.generate(
        sub=f"ADMIN-{ref_token.admin_id}",
        ref_id=ref_token.id,  # type: ignore
    )

    return {
        "data": {
            "admin": await formatters.format_admin(
                # NOTE: this should never return None
                admin=await selectors.get_admin_by_id(id=ref_token.admin_id, db=db)  # type: ignore
            ),
            "tokens": {"access_token": access_token, "refresh_token": ref_token.token},
        }
    }


@router.delete(
    "/logout",
    summary="admin logout",
    response_description="The logout response",
    status_code=200,
    response_model=ResponseSchema,
)
async def route_admin_logout(curr_admin: CurrentAdmin, db: DatabaseSession):
    """
    This endpoint logs out a admin
    """

    # Init crud
    ref_token_crud = AdminRefreshTokenCRUD(db=db)

    # Deactivate refresh tokens
    await ref_token_crud.delete_tokens(Admin=curr_admin)

    return {
        "data": {
            "msg": "admin logged out sucessfully",
        }
    }


@router.get(
    "/me",
    summary="Get Authenticated ADMIN",
    response_description="The Admin profile response",
    status_code=200,
    response_model=response.AdminResponse,
)
async def route_admin_profile(curr_admin: CurrentAdmin, db: DatabaseSession):
    """
    This endpoint displays the current admin's profile
    """

    admin = await selectors.get_admin_by_id(id=curr_admin.id, db=db)

    return {"data": await formatters.format_admin(admin)}
