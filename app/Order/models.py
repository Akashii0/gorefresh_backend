from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
)
from app.Product.models import Product
from app.User.models import User
from app.core.database import DBBase


class OrderItem(DBBase):
    """
    Database model for ordered items
    """

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(
        Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(7, 2), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)

    product: Mapped["Product"] = relationship(
        "Product", backref="order_products", lazy="selectin"
    )


class Order(DBBase):
    """
    Database module for orders
    """

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, nullable=False)
    order_ref = Column(String(12), unique=True, nullable=False)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="SET NULL"))
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    delivery_address = Column(Text, nullable=False)
    additional_info = Column(Text, nullable=True)
    delivery_fee = Column(Numeric(6, 2))
    subtotal = Column(Numeric(10, 2))
    service_fee = Column(Numeric(6, 2))
    total_amount = Column(Numeric(10, 2))
    status = Column(
        Enum(
            "Pending",
            "Confirmed",
            "Preparing",
            "Out for Delivery",
            "Delivered",
            "Cancelled",
            name="enum_order_status",
        ),
        nullable=False,
    )
    payment_method = Column(String(20), nullable=False)

    paystack_reference = Column(String(50), unique=True, nullable=True)
    paystack_token = Column(String(50), nullable=True)
    payment_status = Column(
        Enum("Pending", "Paid", "Failed", name="enum_payment_status"), nullable=False
    )
    estimated_delivery_time = Column(String(50), nullable=False)
    actual_delivery_time = Column(Time(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", backref="user_order", lazy="selectin")

    order_items: Mapped[list[OrderItem]] = relationship(
        "OrderItem", backref="order_food", lazy="selectin"
    )
