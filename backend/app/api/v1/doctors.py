from datetime import date, datetime, time, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.booking import Booking
from app.models.doctor_service import DoctorService
from app.models.slot_reservation import SlotReservation
from app.schemas.doctor import SlotResponse
from app.services.calendly import get_available_slots
from app.services.session import verify_session_token
from app.services.ws_manager import ws_manager

router = APIRouter(prefix="/doctors", tags=["doctors"])

_MAX_DATE_RANGE_DAYS = 7


def _require_user(request: Request) -> str:
    token = request.cookies.get("dentnav_user_id")
    user_id = verify_session_token(token) if token else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id


@router.get("/{doctor_service_id}/availability", response_model=list[SlotResponse])
async def get_availability(
    doctor_service_id: str,
    date_from: Annotated[date, Query()],
    date_to: Annotated[date, Query()],
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[SlotResponse]:
    _require_user(request)

    if (date_to - date_from).days > _MAX_DATE_RANGE_DAYS:
        raise HTTPException(status_code=400, detail=f"Date range cannot exceed {_MAX_DATE_RANGE_DAYS} days")
    if date_to < date_from:
        raise HTTPException(status_code=400, detail="date_to must be >= date_from")

    ds_result = await session.execute(
        select(DoctorService).where(
            DoctorService.id == doctor_service_id,
            DoctorService.is_active == True,
        )
    )
    ds = ds_result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="Doctor service not found")

    doctor = ds.doctor
    if not doctor.is_active or not doctor.calendly_pat:
        raise HTTPException(status_code=404, detail="Doctor not available")

    now = datetime.now(timezone.utc)
    start_dt = datetime.combine(date_from, time.min, tzinfo=timezone.utc)
    end_dt = datetime.combine(date_to, time.max, tzinfo=timezone.utc)
    effective_start = max(start_dt, now + timedelta(minutes=5))

    if effective_start >= end_dt:
        return []

    try:
        raw_slots = await get_available_slots(
            event_type_uri=ds.calendly_event_type_uri,
            pat=doctor.calendly_pat,
            start_time=effective_start,
            end_time=end_dt,
        )
    except Exception as exc:
        import logging
        body = getattr(getattr(exc, "response", None), "text", "")
        logging.getLogger(__name__).error("Calendly availability error: %s | body: %s", exc, body)
        raise HTTPException(status_code=502, detail="Failed to fetch availability from Calendly")

    # Calendly's "start time increment" setting may be shorter than the event duration
    # (e.g. 30-min increments for a 45-min event). Drop any slot that starts within
    # duration_minutes of the previous kept slot so the UI only shows valid windows.
    duration_minutes = ds.service.duration_minutes
    if duration_minutes:
        calendly_slots: list[dict] = []
        last_dt: datetime | None = None
        for slot in raw_slots:
            slot_dt = datetime.fromisoformat(slot["start_time"].replace("Z", "+00:00"))
            if last_dt is None or (slot_dt - last_dt).total_seconds() >= duration_minutes * 60:
                calendly_slots.append(slot)
                last_dt = slot_dt
    else:
        calendly_slots = raw_slots

    # Confirmed bookings — permanently locked
    confirmed_result = await session.execute(
        select(Booking.slot_time).where(
            Booking.doctor_service_id == doctor_service_id,
            Booking.status == "confirmed",
            Booking.slot_time >= start_dt,
            Booking.slot_time <= end_dt,
        )
    )
    booked_slots = {_to_utc(t) for t in confirmed_result.scalars().all()}

    # Pending-payment bookings within active 15-min TTL — show as reserved
    pending_result = await session.execute(
        select(Booking.slot_time).where(
            Booking.doctor_service_id == doctor_service_id,
            Booking.status == "pending_payment",
            Booking.slot_expires_at > now,
            Booking.slot_time >= start_dt,
            Booking.slot_time <= end_dt,
        )
    )
    payment_pending_slots = {_to_utc(t) for t in pending_result.scalars().all()}

    # All active soft locks — include own reservation so API and WS stay consistent
    reserved_result = await session.execute(
        select(SlotReservation.slot_time).where(
            SlotReservation.doctor_service_id == doctor_service_id,
            SlotReservation.expires_at > now,
            SlotReservation.slot_time >= start_dt,
            SlotReservation.slot_time <= end_dt,
        )
    )
    reserved_slots = {_to_utc(t) for t in reserved_result.scalars().all()}

    slots: list[SlotResponse] = []
    for raw in calendly_slots:
        slot_time_str: str = raw["start_time"]
        slot_dt = _to_utc(datetime.fromisoformat(slot_time_str.replace("Z", "+00:00")))

        if slot_dt in booked_slots:
            status = "booked"
        elif slot_dt in reserved_slots or slot_dt in payment_pending_slots:
            status = "reserved"
        else:
            status = "available"

        slots.append(SlotResponse(slot_time=slot_time_str, status=status))

    return slots


@router.websocket("/{doctor_service_id}/availability/ws")
async def availability_ws(doctor_service_id: str, websocket: WebSocket) -> None:
    await ws_manager.connect(doctor_service_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # keep-alive; client messages ignored
    except WebSocketDisconnect:
        ws_manager.disconnect(doctor_service_id, websocket)


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
