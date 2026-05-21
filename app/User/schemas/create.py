from pydantic import BaseModel, EmailStr, Field, field_validator

from app.common.utils import validate_phone_number


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str = Field(description="The Admin's Phone Number", max_length=14)
    password: str = Field(description="The User's raw password")

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
