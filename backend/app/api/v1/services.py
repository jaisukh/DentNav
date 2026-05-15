from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.doctor import Doctor
from app.models.doctor_service import DoctorService
from app.models.service import Service
from app.schemas.service import DoctorForServiceResponse, ServiceResponse

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceResponse])
async def list_services(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[Service]:
    result = await session.execute(
        select(Service).where(Service.is_active == True).order_by(Service.created_at)
    )
    return list(result.scalars().all())


@router.get("/{service_key}/doctors", response_model=list[DoctorForServiceResponse])
async def list_doctors_for_service(
    service_key: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[DoctorForServiceResponse]:
    service_result = await session.execute(
        select(Service).where(Service.service_key == service_key, Service.is_active == True)
    )
    service = service_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    ds_result = await session.execute(
        select(DoctorService)
        .join(Doctor, DoctorService.doctor_id == Doctor.id)
        .where(
            DoctorService.service_id == service.id,
            DoctorService.is_active == True,
            Doctor.is_active == True,
        )
        .order_by(Doctor.name)
    )
    rows = list(ds_result.scalars().all())

    return [
        DoctorForServiceResponse(
            doctor_service_id=ds.id,
            doctor_id=ds.doctor.id,
            name=ds.doctor.name,
            bio=ds.doctor.bio,
            photo_url=ds.doctor.photo_url,
            specializations=ds.doctor.specializations,
            effective_amount=ds.price_override if ds.price_override is not None else service.base_amount,
            currency=service.currency,
        )
        for ds in rows
    ]
