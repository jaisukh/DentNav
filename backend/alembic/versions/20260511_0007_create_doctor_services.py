"""create doctor_services table

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "doctor_services",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("doctor_id", sa.String(36), nullable=False),
        sa.Column("service_id", sa.String(36), nullable=False),
        sa.Column("calendly_event_type_uuid", sa.String(255), nullable=False),
        sa.Column("calendly_event_type_uri", sa.Text(), nullable=False),
        sa.Column("price_override", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
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
        sa.ForeignKeyConstraint(["doctor_id"], ["doctors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("doctor_id", "service_id", name="uq_doctor_service"),
    )
    op.create_index("ix_doctor_services_doctor_id",  "doctor_services", ["doctor_id"])
    op.create_index("ix_doctor_services_service_id", "doctor_services", ["service_id"])


def downgrade() -> None:
    op.drop_index("ix_doctor_services_service_id", table_name="doctor_services")
    op.drop_index("ix_doctor_services_doctor_id",  table_name="doctor_services")
    op.drop_table("doctor_services")
