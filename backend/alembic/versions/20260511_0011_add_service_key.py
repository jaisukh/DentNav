"""add service_key to services

Revision ID: 0011
Revises: 0010
Create Date: 2026-05-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_KEY_MAP = {
    "Analysis Access":           "analysis_access",
    "Introductory Consultation": "intro_consultation",
    "Visa Consultation":         "visa_consultation",
    "Interview Preparation":     "interview_preparation",
    "CV / SOP Review":           "cv_sop_review",
    "CAAPID Assistance":         "caapid_assistance",
    "License Guidance":          "license_guidance",
}


def upgrade() -> None:
    op.add_column("services", sa.Column("service_key", sa.String(100), nullable=True))

    for name, key in _KEY_MAP.items():
        op.execute(
            sa.text("UPDATE services SET service_key = :key WHERE name = :name").bindparams(
                key=key, name=name
            )
        )

    op.alter_column("services", "service_key", nullable=False)
    op.create_unique_constraint("uq_services_service_key", "services", ["service_key"])


def downgrade() -> None:
    op.drop_constraint("uq_services_service_key", "services", type_="unique")
    op.drop_column("services", "service_key")
