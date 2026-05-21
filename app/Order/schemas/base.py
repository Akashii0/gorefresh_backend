from datetime import datetime, time
from typing import List, Optional

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    """
    Base schema for order items
    """

    id: int = Field(description="The ordered item's id")
    order_id: int = Field(description="The order's ID")
    food_item_id: int = Field(description="The food item being ordered")
    food_item_thumbnail: str = Field(description="The thumbnail url of the fooditem")
    food_item_name: str = Field(description="The name of the food item being ordered")
    food_item_category: str = Field(
        description="The category of the food item being ordered"
    )
    quantity: int = Field(gt=0, description="The quantity ordered for the food item")
    unit_price: int = Field(gt=0, description="The individual price of the food item")
    updated_at: datetime | None = Field(description="The updated time")
    created_at: datetime = Field(description="The time the order was created")


class OrderItemSummary(BaseModel):
    """
    Base schema for order item summary
    """

    id: int = Field(description="The ordered item's id")
    food_item_id: int = Field(description="The food item being ordered")
    food_item_thumbnail: str = Field(description="The thumbnail url of the fooditem")
    food_item_name: str = Field(description="The name of the food item being ordered")


class Order(BaseModel):
    """
    Base schema for orders
    """

    id: int = Field(description="The order's ID")
    order_ref: str = Field(description="The order's unique Identifier")
    restaurant_id: int = Field(description="The restaurant's ID")
    restaurant_name: str = Field(description="The restaurant's name")
    # delivery_address_id: int = Field(description="The delivery address's ID")
    delivery_fee: int = Field(description="The delivery fee to be charged")
    service_fee: float = Field(description="The service fee to be charged")
    discount_amount: float = Field(description="The discount fee to be removed")
    subtotal: float = Field(description="The subtotal of the fooditems")
    total_amount: float = Field(description="The total checkout Price")
    email: str = Field(description="The Customer's email")
    full_name: str = Field(description="The Customer's full name")
    phone_number: str = Field(description="The Customer's phone number", max_length=15)
    delivery_address: str = Field(description="Delivery address")
    additional_info: str | None = Field(
        None, description="Optional addition information usually to riders"
    )
    status: str = Field(description="The status of the order")
    payment_method: str = Field(description="Cash or Paystack")
    payment_status: str = Field(description="The status of the transaction")
    estimated_delivery_time: time = Field(description="The estimated time of delivery")
    actual_delivery_time: Optional[time] = Field(
        default=None, description="The actual time of delivery"
    )
    updated_at: datetime | None = Field(description="The updated time")
    created_at: datetime = Field(description="The time the order was created")

    order_items: List[OrderItem] = Field(
        default_factory=list, description="List of main food items in the order"
    )
