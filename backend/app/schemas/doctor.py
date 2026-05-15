from pydantic import BaseModel


class SlotResponse(BaseModel):
    slot_time: str
    status: str  # "available" | "reserved" | "booked"


class DoctorServiceInput(BaseModel):
    service_key: str
    calendly_event_type_uri: str
    price_override: int | None = None


class CreateDoctorRequest(BaseModel):
    name: str
    bio: str = ""
    photo_url: str = ""
    specializations: list[str] = []
    calendly_user_uri: str | None = None
    calendly_pat: str | None = None
    services: list[DoctorServiceInput] = []


class DoctorServiceCreated(BaseModel):
    doctor_service_id: str
    service_key: str
    calendly_event_type_uri: str


class CreateDoctorResponse(BaseModel):
    doctor_id: str
    name: str
    services: list[DoctorServiceCreated]
