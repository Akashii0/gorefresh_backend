"""create cart products table

Revision ID: b6e44c295b68
Revises: ad7e1f293baa
Create Date: 2026-05-15 10:04:38.267466

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b6e44c295b68"
down_revision: Union[str, None] = "ad7e1f293baa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cart_products",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "cart_id",
            sa.Integer,
            sa.ForeignKey("carts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer,
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer, nullable=False, default=1),
        sa.Column("unit_price", sa.Numeric(7, 2), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("cart_products")
