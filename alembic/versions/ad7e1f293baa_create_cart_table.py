"""create cart table

Revision ID: ad7e1f293baa
Revises: cf0801ee83a5
Create Date: 2026-05-15 10:04:10.617666

"""

from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ad7e1f293baa"
down_revision: Union[str, None] = "cf0801ee83a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "carts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id"),
            unique=True,
            nullable=False,
        ),
        sa.Column("delivery_fee", sa.Numeric(6, 2)),
        sa.Column("subtotal", sa.Numeric(10, 2)),
        sa.Column("service_fee", sa.Numeric(6, 2)),
        sa.Column("total_amount", sa.Numeric(10, 2)),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            onupdate=datetime.now(timezone.utc),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("carts")
