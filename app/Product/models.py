from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, relationship

from app.Admin import models as admin_models
from app.core.database import DBBase


class Product(DBBase):
    """
    Database module for productss
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, index=True)
    description = Column(Text, nullable=False)
    thumbnail_url = Column(String, default="/avatar.png", nullable=False)
    price = Column(
        Numeric(7, 2),
        nullable=False,
    )
    rating = Column(Numeric(2, 1), default=3.0, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    product_category_id = Column(
        Integer, ForeignKey("product_categories.id", ondelete="CASCADE"), nullable=False
    )
    no_orders = Column(Integer, default=0, nullable=False)
    no_ratings = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    created_by = Column(
        Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped["ProductCategory"] = relationship(
        "ProductCategory", backref="product_in_category", lazy="selectin"
    )
    admin: Mapped[admin_models.Admin] = relationship(
        "Admin", backref="product_created_by_admin", lazy="selectin"
    )


class ProductCategory(DBBase):
    """
    Database model for product categories
    """

    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thumbnail_url = Column(String, default="/avatar.png", nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    created_by = Column(
        Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False
    )

    admin: Mapped[admin_models.Admin] = relationship(
        "Admin", backref="product_category_created_by_admin", lazy="selectin"
    )


class ProductRating(DBBase):
    """
    Database model for Products ratings
    """

    __tablename__ = "product_ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    rating = Column(Integer, nullable=False)  # 1 to 5
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
