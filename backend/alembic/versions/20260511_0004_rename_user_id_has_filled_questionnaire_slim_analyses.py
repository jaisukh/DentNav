"""rename user.id->user_id, has_filled->has_filled_questionnaire; slim analyses table

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-11

Changes:
  users: id -> user_id, has_filled -> has_filled_questionnaire
  analyses: drop paid/country/degree/years_of_exp columns, rename payload -> llm_result,
            update FK reference to users.user_id
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── analyses: drop FK before renaming the referenced column ──────────────
    op.drop_constraint("analyses_user_id_fkey", "analyses", type_="foreignkey")

    # ── users: rename primary key column ─────────────────────────────────────
    op.alter_column("users", "id", new_column_name="user_id")

    # ── users: rename has_filled -> has_filled_questionnaire ─────────────────
    op.alter_column("users", "has_filled", new_column_name="has_filled_questionnaire")

    # ── analyses: rename payload -> llm_result ────────────────────────────────
    op.alter_column("analyses", "payload", new_column_name="llm_result")

    # ── analyses: drop columns no longer stored on the row ───────────────────
    op.drop_column("analyses", "paid")
    op.drop_column("analyses", "country")
    op.drop_column("analyses", "degree")
    op.drop_column("analyses", "years_of_exp")

    # ── analyses: restore FK pointing at the renamed PK ──────────────────────
    op.create_foreign_key(
        "analyses_user_id_fkey",
        "analyses",
        "users",
        ["user_id"],
        ["user_id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("analyses_user_id_fkey", "analyses", type_="foreignkey")

    # Restore dropped analyses columns
    op.add_column(
        "analyses",
        sa.Column("years_of_exp", sa.String(length=120), server_default="", nullable=False),
    )
    op.add_column(
        "analyses",
        sa.Column("degree", sa.String(length=120), server_default="", nullable=False),
    )
    op.add_column(
        "analyses",
        sa.Column("country", sa.String(length=120), server_default="", nullable=False),
    )
    op.add_column(
        "analyses",
        sa.Column("paid", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.alter_column("analyses", "years_of_exp", server_default=None)
    op.alter_column("analyses", "degree", server_default=None)
    op.alter_column("analyses", "country", server_default=None)
    op.alter_column("analyses", "paid", server_default=None)

    # Rename llm_result back to payload
    op.alter_column("analyses", "llm_result", new_column_name="payload")

    # Rename users columns back
    op.alter_column("users", "has_filled_questionnaire", new_column_name="has_filled")
    op.alter_column("users", "user_id", new_column_name="id")

    # Restore FK
    op.create_foreign_key(
        "analyses_user_id_fkey",
        "analyses",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )
