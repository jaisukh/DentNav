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
