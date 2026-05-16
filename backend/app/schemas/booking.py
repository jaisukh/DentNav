from datetime import datetime

from pydantic import BaseModel


class ReserveRequest(BaseModel):
    doctor_service_id: str
    slot_time: datetime


class ReserveResponse(BaseModel):
    reservation_id: str
    slot_time: datetime
    expires_at: datetime


class ReleaseRequest(BaseModel):
    reservation_id: str


class MyBookingResponse(BaseModel):
    id: str
    status: str
    slot_time: datetime | None
    doctor_name: str
    service_name: str
    duration_minutes: int | None
    calendly_invitee_uri: str | None = None
