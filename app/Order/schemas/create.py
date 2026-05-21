from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class OrderItemCreate(BaseModel):
    """
    Create schema for Order items
    """

    product_id: int = Field(description="The product being ordered")
    quantity: int = Field(description="Quantity ordered")


class CartOrderCreate(BaseModel):
    """
    Create schema for Orders from cart
    """

    cart_id: int = Field(description="The cart's ID")
    payment_method: str = Field(description="Transfer or Paystack")
    delivery_address: str = Field(description="Delivery address")
    additional_info: str | None = Field(
        None, description="Optional addition information usually to riders"
    )
    # coupon_code: str | None = Field(
    #     None, description="Optional coupon code to apply discount"
    # )

    @field_validator("payment_method")
    def validate_payment_method(cls, v):
        if v.lower() not in {"transfer", "paystack"}:
            raise ValueError("Must be 'Transfer' or 'Paystack'")
        return v.title()


class OrderCreate(BaseModel):
    """
    Create schema for Orders
    """

    user_id: int = Field(description="The user's ID")
    payment_method: str = Field(description="Cash or Paystack")
    order_items: Optional[List[OrderItemCreate]] = Field(
        default=None, description="Optional list of products in the order"
    )

    @field_validator("payment_method")
    def validate_payment_method(cls, v):
        if v.lower() not in {"cash", "paystack"}:
            raise ValueError("Must be 'Cash' or 'Paystack'")
        return v.title()

    @model_validator(mode="after")
    def validate_non_empty_order(self):
        order_items = self.order_items if self.order_items is not None else []

        if not order_items:
            raise ValueError("Order must contain at least one item")
        return self
