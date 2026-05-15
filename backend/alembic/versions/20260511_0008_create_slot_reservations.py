"""create slot_reservations table

Revision ID: 0008
Revises: 0007
Create Date: 2026-05-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "slot_reservations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("doctor_service_id", sa.String(36), nullable=False),
        sa.Column("slot_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["doctor_service_id"], ["doctor_services.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.user_id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint(
            "doctor_service_id", "slot_time", name="uq_slot_reservation"
        ),
    )
    op.create_index("ix_slot_reservations_user_id",    "slot_reservations", ["user_id"])
    op.create_index("ix_slot_reservations_expires_at", "slot_reservations", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_slot_reservations_expires_at", table_name="slot_reservations")
    op.drop_index("ix_slot_reservations_user_id",    table_name="slot_reservations")
    op.drop_table("slot_reservations")
