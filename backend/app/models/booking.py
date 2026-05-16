from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False
    )
    doctor_service_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("doctor_services.id", ondelete="RESTRICT"), nullable=False
    )
    payment_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("payments.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="pending_payment", nullable=False
    )
    slot_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    slot_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    calendly_event_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    calendly_invitee_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
