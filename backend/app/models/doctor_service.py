from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DoctorService(Base):
    __tablename__ = "doctor_services"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    doctor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    service_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("services.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    calendly_event_type_uuid: Mapped[str] = mapped_column(String(255), nullable=False)
    calendly_event_type_uri: Mapped[str] = mapped_column(Text, nullable=False)
    price_override: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    doctor: Mapped["Doctor"] = relationship("Doctor", lazy="joined")  # type: ignore[name-defined]
    service: Mapped["Service"] = relationship("Service", lazy="joined")  # type: ignore[name-defined]
