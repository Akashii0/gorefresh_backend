"""create product categories table

Revision ID: dd1c34e91ed5
Revises: b9328a0561a5
Create Date: 2026-05-05 21:04:44.650495

"""

from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dd1c34e91ed5"
down_revision: Union[str, None] = "b9328a0561a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_categories",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("thumbnail_url", sa.String, default="/avatar.png", nullable=False),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
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
    op.drop_table("product_categories")
