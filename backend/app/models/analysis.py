from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Analysis(Base):
    """
    Server-side store for the full LLM analysis payload.

    Privacy boundary: the API only returns a *preview* slice (readiness score,
    dimensions, strengths, gaps, profile snapshot) to the client until the
    user has signed in AND paid. The full `payload` is only released through
    `GET /api/v1/analysis/{id}/full`.
    """

    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    country: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    degree: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    years_of_exp: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    performance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    answers: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
