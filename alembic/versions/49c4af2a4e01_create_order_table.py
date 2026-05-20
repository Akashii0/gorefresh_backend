from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

revision: str = "49c4af2a4e01"
down_revision: Union[str, None] = "b6e44c295b68"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create ENUM types safely (works on all PostgreSQL versions)
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'enum_order_status') THEN
                CREATE TYPE enum_order_status AS ENUM (
                    'Pending', 'Confirmed', 'Preparing', 'Out for Delivery', 'Delivered', 'Cancelled'
                );
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'enum_payment_status') THEN
                CREATE TYPE enum_payment_status AS ENUM (
                    'Pending', 'Paid', 'Failed'
                );
            END IF;
        END $$;
    """)

    # 2. Create table using the existing ENUM types (create_type=False)
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("order_ref", sa.String(12), unique=True, nullable=False),
        sa.Column(
            "cart_id", sa.Integer, sa.ForeignKey("carts.id", ondelete="SET NULL")
        ),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("delivery_address", sa.Text, nullable=False),
        sa.Column("additional_info", sa.Text, nullable=True),
        sa.Column("delivery_fee", sa.Numeric(6, 2), nullable=True),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=True),
        sa.Column("service_fee", sa.Numeric(6, 2), nullable=True),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=True),
        sa.Column(
            "status",
            PG_ENUM(
                "Pending",
                "Confirmed",
                "Preparing",
                "Out for Delivery",
                "Delivered",
                "Cancelled",
                name="enum_order_status",
                create_type=False,  # ← critical
            ),
            nullable=False,
        ),
        sa.Column("payment_method", sa.String(20), nullable=False),
        sa.Column("payment_reference", sa.String(50), nullable=False),
        sa.Column("payment_token", sa.String(50), nullable=False),
        sa.Column(
            "payment_status",
            PG_ENUM(
                "Pending",
                "Paid",
                "Failed",
                name="enum_payment_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("estimated_delivery_time", sa.String(50), nullable=False),
        sa.Column("actual_delivery_time", sa.Time(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("orders")
    op.execute("DROP TYPE IF EXISTS enum_order_status;")
    op.execute("DROP TYPE IF EXISTS enum_payment_status;")
