import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.booking import Booking
from app.models.doctor_service import DoctorService
from app.models.slot_reservation import SlotReservation
from app.schemas.booking import MyBookingResponse, ReleaseRequest, ReserveRequest, ReserveResponse
from app.services.session import verify_session_token
from app.services.ws_manager import ws_manager

router = APIRouter(prefix="/bookings", tags=["bookings"])

_RESERVATION_TTL_MINUTES = 5


def _require_user(request: Request) -> str:
    token = request.cookies.get("dentnav_user_id")
    user_id = verify_session_token(token) if token else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id


@router.get("/my", response_model=list[MyBookingResponse])
async def my_bookings(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[MyBookingResponse]:
    user_id = _require_user(request)

    result = await session.execute(
        select(Booking, DoctorService)
        .join(DoctorService, Booking.doctor_service_id == DoctorService.id)
        .where(
            Booking.user_id == user_id,
            Booking.status.in_(["confirmed", "completed", "no_show"]),
        )
        .order_by(Booking.created_at.desc())
    )
    rows = result.all()

    return [
        MyBookingResponse(
            id=booking.id,
            status=booking.status,
            slot_time=booking.slot_time,
            doctor_name=ds.doctor.name if ds.doctor else "",
            service_name=ds.service.name if ds.service else "",
            duration_minutes=ds.service.duration_minutes if ds.service else None,
            calendly_invitee_uri=booking.calendly_invitee_uri,
        )
        for booking, ds in rows
    ]


@router.post("/reserve", response_model=ReserveResponse)
async def reserve_slot(
    body: ReserveRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReserveResponse:
    user_id = _require_user(request)

    # Validate doctor_service exists and is active
    ds_result = await session.execute(
        select(DoctorService).where(
            DoctorService.id == body.doctor_service_id,
            DoctorService.is_active,
        )
    )
    if not ds_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Doctor service not found")

    # Guard: slot already has a confirmed/completed booking
    confirmed = await session.execute(
        select(Booking.id).where(
            Booking.doctor_service_id == body.doctor_service_id,
            Booking.slot_time == body.slot_time,
            Booking.status.in_(["confirmed", "completed"]),
        )
    )
    if confirmed.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="slot_already_booked")

    # Atomic conditional upsert — only overwrites an expired reservation
    new_id = str(uuid.uuid4())
    expires_at = datetime.now(UTC) + timedelta(minutes=_RESERVATION_TTL_MINUTES)

    stmt = (
        pg_insert(SlotReservation)
        .values(
            id=new_id,
            doctor_service_id=body.doctor_service_id,
            slot_time=body.slot_time,
            user_id=user_id,
            expires_at=expires_at,
        )
        .on_conflict_do_update(
            constraint="uq_slot_reservation",
            set_={
                "id": new_id,
                "user_id": user_id,
                "expires_at": expires_at,
            },
            where=SlotReservation.expires_at <= func.now(),
        )
        .returning(SlotReservation.id, SlotReservation.expires_at)
    )

    result = await session.execute(stmt)
    row = result.fetchone()

    if row is None:
        raise HTTPException(status_code=409, detail="slot_taken")

    reservation_id, actual_expires_at = row

    # Release any prior reservation this user held for the same doctor_service
    # (user switched slots before paying)
    await session.execute(
        delete(SlotReservation).where(
            SlotReservation.doctor_service_id == body.doctor_service_id,
            SlotReservation.user_id == user_id,
            SlotReservation.id != reservation_id,
        )
    )

    await session.commit()

    await ws_manager.broadcast(
        body.doctor_service_id,
        body.slot_time.isoformat(),
        "reserved",
    )

    return ReserveResponse(
        reservation_id=reservation_id,
        slot_time=body.slot_time,
        expires_at=actual_expires_at,
    )


@router.post("/reserve/release")
async def release_slot(
    body: ReleaseRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    user_id = _require_user(request)

    res_result = await session.execute(
        select(SlotReservation).where(
            SlotReservation.id == body.reservation_id,
            SlotReservation.user_id == user_id,
        )
    )
    reservation = res_result.scalar_one_or_none()

    if reservation:
        doctor_service_id = reservation.doctor_service_id
        slot_time = reservation.slot_time.isoformat()
        await session.delete(reservation)
        await session.commit()
        await ws_manager.broadcast(doctor_service_id, slot_time, "available")

    return {"ok": True}
