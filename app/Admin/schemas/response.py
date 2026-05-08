from pydantic import Field

from app.common.schemas import ResponseSchema
from app.Admin.schemas.base import Admin, AdminLogin


class AdminLoginResponse(ResponseSchema):
    """
    Response schema for admin login
    """

    data: AdminLogin = Field(description="The login details")


class AdminResponse(ResponseSchema):
    """
    Response schema for admins
    """

    msg: str = "admin retrieved successfully"
    data: Admin = Field(description="The admin's details")
