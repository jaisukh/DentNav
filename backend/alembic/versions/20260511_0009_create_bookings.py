"""create bookings table

Revision ID: 0009
Revises: 0008
Create Date: 2026-05-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bookings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("doctor_service_id", sa.String(36), nullable=False),
        sa.Column("payment_id", sa.String(36), nullable=True),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="pending_payment",
        ),
        sa.Column("slot_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("slot_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("calendly_event_uri", sa.Text(), nullable=True),
        sa.Column("calendly_invitee_uri", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
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
        # payment_id FK added after payments table exists (migration 0010)
    )
    op.create_index("ix_bookings_user_id",           "bookings", ["user_id"])
    op.create_index("ix_bookings_doctor_service_id", "bookings", ["doctor_service_id"])
    op.create_index("ix_bookings_status",            "bookings", ["status"])


def downgrade() -> None:
    op.drop_index("ix_bookings_status",            table_name="bookings")
    op.drop_index("ix_bookings_doctor_service_id", table_name="bookings")
    op.drop_index("ix_bookings_user_id",           table_name="bookings")
    op.drop_table("bookings")
