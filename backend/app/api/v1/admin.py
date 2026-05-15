import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_session
from app.models.doctor import Doctor
from app.models.doctor_service import DoctorService
from app.models.service import Service
from app.schemas.doctor import CreateDoctorRequest, CreateDoctorResponse, DoctorServiceCreated

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_admin(x_admin_key: Annotated[str | None, Header()] = None) -> None:
    if not settings.admin_api_key:
        raise HTTPException(status_code=503, detail="Admin API not configured")
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid admin key")


def _uuid_from_uri(uri: str) -> str:
    """Extract the UUID segment from the last path component of a Calendly URI."""
    return uri.rstrip("/").rsplit("/", 1)[-1]


@router.post("/doctors", response_model=CreateDoctorResponse, status_code=201)
async def create_doctor(
    body: CreateDoctorRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[None, Depends(_require_admin)],
) -> CreateDoctorResponse:
    doctor_id = str(uuid.uuid4())
    doctor = Doctor(
        id=doctor_id,
        name=body.name,
        bio=body.bio,
        photo_url=body.photo_url,
        specializations=body.specializations,
        calendly_user_uri=body.calendly_user_uri,
        calendly_pat=body.calendly_pat,
        is_active=True,
    )
    session.add(doctor)

    created_services: list[DoctorServiceCreated] = []

    for svc_input in body.services:
        svc_result = await session.execute(
            select(Service).where(Service.service_key == svc_input.service_key)
        )
        service = svc_result.scalar_one_or_none()
        if not service:
            raise HTTPException(
                status_code=422,
                detail=f"Service with key '{svc_input.service_key}' not found",
            )

        ds_id = str(uuid.uuid4())
        ds = DoctorService(
            id=ds_id,
            doctor_id=doctor_id,
            service_id=service.id,
            calendly_event_type_uri=svc_input.calendly_event_type_uri,
            calendly_event_type_uuid=_uuid_from_uri(svc_input.calendly_event_type_uri),
            price_override=svc_input.price_override,
            is_active=True,
        )
        session.add(ds)
        created_services.append(
            DoctorServiceCreated(
                doctor_service_id=ds_id,
                service_key=svc_input.service_key,
                calendly_event_type_uri=svc_input.calendly_event_type_uri,
            )
        )

    await session.commit()

    return CreateDoctorResponse(
        doctor_id=doctor_id,
        name=body.name,
        services=created_services,
    )
