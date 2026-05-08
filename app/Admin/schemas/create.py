from pydantic import BaseModel, EmailStr, Field, field_validator

from app.common.utils import validate_phone_number


class AdminCreate(BaseModel):
    """
    Create schema for Admins
    """

    first_name: str = Field(description="The Admin's First Name", max_length=50)
    last_name: str = Field(description="The Admin's Last Name", max_length=50)
    email: EmailStr = Field(description="The Admin's email Address")
    phone: str = Field(description="The Admin's Phone Number", max_length=14)
    password: str = Field(description="The Admin's raw password")

    @field_validator("email")
    def validate_email(cls, v: str):
        """
        Field validator for email
        """
        return v.lower()

    @field_validator("phone")
    def validate_phone_numbers(cls, v: str):
        """
        Tasks:
            - Checks if the phone number is valid
        """
        if not v:
            return v

        if validate_phone_number(phone_number=v):
            return v
        raise ValueError("Invalid phone number")
