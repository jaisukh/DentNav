"""create services table and seed rows

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SEED = [
    # (name, duration_minutes, base_amount)
    ("Analysis Access",            None, 0),
    ("Introductory Consultation",  45,   0),
    ("Visa Consultation",          60,   0),
    ("Interview Preparation",      60,   0),
    ("CV / SOP Review",            60,   0),
    ("CAAPID Assistance",          60,   0),
    ("License Guidance",           60,   0),
]


def upgrade() -> None:
    op.create_table(
        "services",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("base_amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="usd"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO services (id, name, duration_minutes, base_amount, currency)
            VALUES
              (gen_random_uuid(), 'Analysis Access',            NULL, 0, 'usd'),
              (gen_random_uuid(), 'Introductory Consultation',  45,   0, 'usd'),
              (gen_random_uuid(), 'Visa Consultation',          60,   0, 'usd'),
              (gen_random_uuid(), 'Interview Preparation',      60,   0, 'usd'),
              (gen_random_uuid(), 'CV / SOP Review',            60,   0, 'usd'),
              (gen_random_uuid(), 'CAAPID Assistance',          60,   0, 'usd'),
              (gen_random_uuid(), 'License Guidance',           60,   0, 'usd')
            """
        )
    )


def downgrade() -> None:
    op.drop_table("services")
