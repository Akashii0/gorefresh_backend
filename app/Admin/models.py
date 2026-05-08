from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from app.core.database import DBBase


class Admin(DBBase):
    """
    Database model for admins
    """

    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    pfp_url = Column(String, nullable=False, default="/avatar.png")
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(15), unique=True, nullable=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)


class AdminRefreshToken(DBBase):
    """
    Database model for Admin refresh tokens
    """

    __tablename__ = "admin_refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(
        Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False
    )
    token = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
