"""add phone to users table

Revision ID: 3486b5ea9006
Revises: 94d1dba32782
Create Date: 2026-05-21 18:58:25.737515

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3486b5ea9006"
down_revision: Union[str, None] = "94d1dba32782"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("phone", sa.String(15), unique=True, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "phone")
