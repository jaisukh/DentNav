"""users: first/last name, has_filled; drop token

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-27

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("first_name", sa.String(length=120), server_default="", nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("last_name", sa.String(length=120), server_default="", nullable=False),
    )
    op.add_column(
        "users",
        sa.Column(
            "has_filled",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    # Denormalize: anyone who already has a claimed analysis has filled the questionnaire
    op.execute(
        sa.text(
            "UPDATE users SET has_filled = true "
            "WHERE id IN (SELECT DISTINCT user_id FROM analyses WHERE user_id IS NOT NULL)"
        )
    )
    op.alter_column("users", "first_name", server_default=None)
    op.alter_column("users", "last_name", server_default=None)
    op.alter_column("users", "has_filled", server_default=None)
    op.drop_column("users", "token")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("token", sa.Text(), nullable=False, server_default=""),
    )
    op.alter_column("users", "token", server_default=None)
    op.drop_column("users", "has_filled")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
