"""create admins table

Revision ID: cec8a11fe2b1
Revises: 4acfe5d185fe
Create Date: 2026-05-05 20:50:56.329081

"""

from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cec8a11fe2b1"
down_revision: Union[str, None] = "4acfe5d185fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admins",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("pfp_url", sa.String, nullable=False, default="/avatar.png"),
        sa.Column("first_name", sa.String(50), nullable=True),
        sa.Column("last_name", sa.String(50), nullable=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("phone", sa.String(15), unique=True, nullable=True),
        sa.Column("password", sa.String, nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
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
    )


def downgrade() -> None:
    op.drop_table("admins")
