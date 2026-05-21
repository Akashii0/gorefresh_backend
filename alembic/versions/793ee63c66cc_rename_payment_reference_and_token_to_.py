"""rename payment reference and token to paystack in orders table

Revision ID: 793ee63c66cc
Revises: 3486b5ea9006
Create Date: 2026-05-21 19:53:19.882265

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "793ee63c66cc"
down_revision: Union[str, None] = "3486b5ea9006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Rename payment_reference -> paystack_reference, make nullable
    op.alter_column(
        "orders",
        "payment_reference",
        new_column_name="paystack_reference",
        existing_type=sa.String(50),
        existing_nullable=False,  # original was NOT NULL
        nullable=True,  # <-- add this to make it nullable after rename
    )

    # Rename payment_token -> paystack_token, make nullable
    op.alter_column(
        "orders",
        "payment_token",
        new_column_name="paystack_token",
        existing_type=sa.String(50),
        existing_nullable=False,
        nullable=True,  # <-- add this
    )


def downgrade():
    # Revert the renames
    op.alter_column(
        "orders",
        "paystack_reference",
        new_column_name="payment_reference",
        existing_type=sa.String(50),
        existing_nullable=True,  # current nullable
        nullable=False,  # revert to NOT NULL
    )

    op.alter_column(
        "orders",
        "paystack_token",
        new_column_name="payment_token",
        existing_type=sa.String(50),
        existing_nullable=True,
        nullable=False,
    )
