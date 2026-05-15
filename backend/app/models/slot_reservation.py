from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SlotReservation(Base):
    __tablename__ = "slot_reservations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    doctor_service_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("doctor_services.id", ondelete="CASCADE"), nullable=False
    )
    slot_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
