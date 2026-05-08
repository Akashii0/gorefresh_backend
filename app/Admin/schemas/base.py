from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.common.schemas import Token


class Admin(BaseModel):
    """
    Base schemas for Admins
    """

    id: int = Field(description="The Admin's ID")
    pfp_url: str = Field(description="The url of the Admin's profile pic")
    first_name: str = Field(description="The Admin's first name")
    last_name: str = Field(description="The Admin's last name")
    email: str = Field(description="The Admin's email address")
    phone: str = Field(description="The Admin's phone number")
    is_active: bool = Field(description="Whether the Admin is active or not")
    last_login: datetime | None = Field(description="The Admin's last login")
    updated_at: datetime | None = Field(
        default=None, description="The Admin's last update date"
    )
    created_at: datetime = Field(description="The Admin's creation date")


class AdminLoginCredentials(BaseModel):
    """
    Base schema for login credentials
    """

    email: EmailStr = Field(description="The Admin's email address")
    password: str = Field(description="The Admin's Raw password")


class AdminLogin(BaseModel):
    """
    Base schema for Admin login response
    """

    admin: Admin = Field(description="The Admin's details")
    tokens: Token = Field(description="The auth token")


class AdminSummary(BaseModel):
    """
    Base schema for admin summary
    """

    id: int = Field(description="The admin's ID")
    pfp_url: str = Field(description="The url of the admin's profile pic")
    full_name: str = Field(description="The admin's full name")
