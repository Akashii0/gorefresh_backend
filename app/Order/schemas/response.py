from pydantic import Field

from app.common.schemas import ResponseSchema
from app.order.schemas.base import Order, OrderItem


class OrderItemResponse(ResponseSchema):
    """
    Response schema for order items
    """

    msg: str = Field(default="Order item retrieved successfully")
    data: OrderItem = Field(description="The details of the order item")


class OrderResponse(ResponseSchema):
    """
    Response schema for orders
    """

    msg: str = Field(default="Order retrieved successfully")
    data: Order = Field(description="The details of the order")
