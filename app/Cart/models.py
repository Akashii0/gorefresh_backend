from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric
from app.core.database import DBBase
from sqlalchemy.orm import Mapped, relationship
from app.Product.models import Product


class Cart(DBBase):
    """
    Database module for carts
    """

    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    delivery_fee = Column(Numeric(6, 2))
    subtotal = Column(Numeric(10, 2))
    service_fee = Column(Numeric(6, 2))
    total_amount = Column(Numeric(10, 2))
    updated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    products: Mapped[list["CartProduct"]] = relationship(
        "CartProduct",
        back_populates="cart",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class CartProduct(DBBase):
    """
    Database model for cart product
    """

    __tablename__ = "cart_products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(
        Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False
    )
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(7, 2), nullable=False)

    product: Mapped["Product"] = relationship(
        "Product", backref="cart_products", lazy="selectin"
    )

    cart: Mapped["Cart"] = relationship("Cart", back_populates="products")
