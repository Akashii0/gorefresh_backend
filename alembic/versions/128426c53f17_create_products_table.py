"""create products table

Revision ID: 128426c53f17
Revises: dd1c34e91ed5
Create Date: 2026-05-05 21:09:24.086977

"""

from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "128426c53f17"
down_revision: Union[str, None] = "dd1c34e91ed5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True, nullable=False),
        sa.Column("name", sa.String, index=True),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("thumbnail_url", sa.String, default="/avatar.png", nullable=False),
        sa.Column(
            "price",
            sa.Numeric(7, 2),
            nullable=False,
        ),
        sa.Column(
            "product_category_id",
            sa.Integer,
            sa.ForeignKey("product_categories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rating", sa.Numeric(2, 1), default=3.0, nullable=False),
        sa.Column("is_available", sa.Boolean, default=True, nullable=False),
        sa.Column("no_orders", sa.Integer, default=0, nullable=False),
        sa.Column("no_ratings", sa.Integer, default=0, nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            onupdate=datetime.now,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            sa.Integer,
            sa.ForeignKey("admins.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("products")
