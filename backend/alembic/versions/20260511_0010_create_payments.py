"""create payments table and wire bookings.payment_id FK

Revision ID: 0010
Revises: 0009
Create Date: 2026-05-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("doctor_service_id", sa.String(36), nullable=True),
        sa.Column("reference_id", sa.String(36), nullable=True),
        sa.Column("razorpay_order_id", sa.String(255), nullable=False),
        sa.Column("razorpay_payment_id", sa.String(255), nullable=True),
        sa.Column("razorpay_signature", sa.String(512), nullable=True),
        sa.Column("amount", sa.Integer, nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, server_default="usd"),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["doctor_service_id"], ["doctor_services.id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("razorpay_order_id", name="uq_payments_razorpay_order_id"),
        sa.UniqueConstraint("razorpay_payment_id", name="uq_payments_razorpay_payment_id"),
    )
    op.create_index("ix_payments_user_id", "payments", ["user_id"])
    op.create_index("ix_payments_status", "payments", ["status"])

    # Partial unique index: one succeeded analysis payment per reference_id
    op.execute(sa.text(
        "CREATE UNIQUE INDEX uq_payments_analysis_succeeded "
        "ON payments (reference_id) "
        "WHERE doctor_service_id IS NULL AND status = 'succeeded'"
    ))

    # Deferred FK from migration 0009: bookings.payment_id → payments.id
    op.create_foreign_key(
        "bookings_payment_id_fkey",
        "bookings", "payments",
        ["payment_id"], ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("bookings_payment_id_fkey", "bookings", type_="foreignkey")
    op.execute(sa.text("DROP INDEX IF EXISTS uq_payments_analysis_succeeded"))
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_user_id", table_name="payments")
    op.drop_table("payments")
