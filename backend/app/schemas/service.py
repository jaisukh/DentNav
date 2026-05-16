from pydantic import BaseModel, computed_field


class ServiceResponse(BaseModel):
    id: str
    service_key: str
    name: str
    description: str
    duration_minutes: int | None
    base_amount: int
    currency: str = "usd"
    is_active: bool

    @computed_field
    @property
    def is_consultation(self) -> bool:
        return self.duration_minutes is not None

    model_config = {"from_attributes": True}


class DoctorForServiceResponse(BaseModel):
    doctor_service_id: str
    doctor_id: str
    name: str
    bio: str
    photo_url: str
    specializations: list[str]
    effective_amount: int
    currency: str

    model_config = {"from_attributes": True}
