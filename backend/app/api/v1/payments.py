import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

_log = logging.getLogger(__name__)

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_session
from app.models.booking import Booking
from app.models.doctor_service import DoctorService
from app.models.payment import Payment
from app.models.slot_reservation import SlotReservation
from app.schemas.payment import (
    CancelOrderRequest,
    CreateOrderRequest,
    CreateOrderResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
)
from app.services import razorpay_client
from app.services.session import verify_session_token
from app.services.ws_manager import ws_manager

router = APIRouter(prefix="/payments", tags=["payments"])

_BOOKING_TTL_MINUTES = 10


def _require_user(request: Request) -> str:
    token = request.cookies.get("dentnav_user_id")
    user_id = verify_session_token(token) if token else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id


@router.post("/create-order", response_model=CreateOrderResponse)
async def create_order(
    body: CreateOrderRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateOrderResponse:
    user_id = _require_user(request)

    if not settings.has_razorpay_config:
        raise HTTPException(status_code=503, detail="Payment gateway not configured")

    # Verify active slot reservation for this user
    res_result = await session.execute(
        select(SlotReservation).where(
            SlotReservation.doctor_service_id == body.doctor_service_id,
            SlotReservation.slot_time == body.slot_time,
            SlotReservation.user_id == user_id,
            SlotReservation.expires_at > datetime.now(timezone.utc),
        )
    )
    reservation = res_result.scalar_one_or_none()
    if not reservation:
        raise HTTPException(
            status_code=409,
            detail="reservation_expired",
        )

    # Load doctor_service + service for price resolution
    ds_result = await session.execute(
        select(DoctorService).where(DoctorService.id == body.doctor_service_id)
    )
    ds = ds_result.scalar_one_or_none()
    if not ds:
        raise HTTPException(status_code=404, detail="Doctor service not found")

    amount = ds.price_override if ds.price_override is not None else ds.service.base_amount
    currency = ds.service.currency

    slot_expires_at = datetime.now(timezone.utc) + timedelta(minutes=_BOOKING_TTL_MINUTES)

    booking_id = str(uuid.uuid4())
    payment_id = str(uuid.uuid4())

    # Create Razorpay order first — we need its ID before inserting the payment row
    try:
        order = razorpay_client.create_order(
            amount=amount,
            currency=currency,
            receipt=payment_id,
            notes={
                "payment_id": payment_id,
                "booking_id": booking_id,
                "user_id": user_id,
            },
        )
    except Exception as exc:
        _log.error("Razorpay create_order failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail="Failed to create payment order")

    # Create booking + payment rows atomically, with razorpay_order_id already set
    booking = Booking(
        id=booking_id,
        user_id=user_id,
        doctor_service_id=body.doctor_service_id,
        status="pending_payment",
        slot_time=body.slot_time,
        slot_expires_at=slot_expires_at,
    )
    session.add(booking)

    payment = Payment(
        id=payment_id,
        user_id=user_id,
        doctor_service_id=body.doctor_service_id,
        reference_id=booking_id,
        razorpay_order_id=order["id"],
        amount=amount,
        currency=currency,
        status="pending",
    )
    session.add(payment)

    # Release slot reservation — booking is now the lock
    slot_time_iso = body.slot_time.isoformat()
    await session.delete(reservation)
    await session.commit()

    await ws_manager.broadcast(body.doctor_service_id, slot_time_iso, "booked")

    return CreateOrderResponse(
        order_id=order["id"],
        amount=amount,
        currency=currency,
        booking_id=booking_id,
        expires_at=slot_expires_at,
    )


@router.post("/cancel-order", status_code=200)
async def cancel_order(
    body: CancelOrderRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    user_id = _require_user(request)

    result = await session.execute(
        select(Booking).where(
            Booking.id == body.booking_id,
            Booking.user_id == user_id,
            Booking.status == "pending_payment",
        )
    )
    booking = result.scalar_one_or_none()
    if not booking:
        return {"ok": True}  # already cancelled / not found — idempotent

    doctor_service_id = booking.doctor_service_id
    slot_time_iso = booking.slot_time.isoformat()

    now = datetime.now(timezone.utc)
    await session.execute(
        update(Booking)
        .where(Booking.id == body.booking_id)
        .values(status="cancelled", updated_at=now)
    )
    await session.commit()

    await ws_manager.broadcast(doctor_service_id, slot_time_iso, "available")
    return {"ok": True}


@router.post("/verify", response_model=VerifyPaymentResponse)
async def verify_payment(
    body: VerifyPaymentRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> VerifyPaymentResponse:
    _require_user(request)

    # Step 1 — HMAC signature check (before any DB write)
    if not razorpay_client.verify_signature(
        body.razorpay_order_id, body.razorpay_payment_id, body.razorpay_signature
    ):
        raise HTTPException(status_code=400, detail="signature_mismatch")

    # Step 2 — Load payment by order ID
    pay_result = await session.execute(
        select(Payment).where(Payment.razorpay_order_id == body.razorpay_order_id)
    )
    payment = pay_result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="payment_not_found")

    # Idempotency — already confirmed (e.g. webhook arrived first)
    if payment.status == "succeeded":
        booking = await session.get(Booking, payment.reference_id)
        ds = await session.get(DoctorService, booking.doctor_service_id)
        return VerifyPaymentResponse(
            ok=True,
            booking_id=booking.id,
            slot_time=booking.slot_time,
            doctor_name=ds.doctor.name if ds else "",
            calendly_invitee_uri=booking.calendly_invitee_uri,
        )

    # Step 3 — Atomic slot confirm (eliminates TOCTOU race)
    now = datetime.now(timezone.utc)
    confirm_stmt = (
        update(Booking)
        .where(
            Booking.id == payment.reference_id,
            Booking.status == "pending_payment",
            Booking.slot_expires_at > now,
        )
        .values(status="confirmed", payment_id=payment.id, updated_at=now)
        .returning(Booking.id, Booking.slot_time, Booking.doctor_service_id)
    )
    confirm_result = await session.execute(confirm_stmt)
    booking_row = confirm_result.fetchone()

    if booking_row is None:
        # Slot expired — mark refund_pending first, then initiate with Razorpay
        # If the Razorpay call succeeds, refund.processed webhook will flip to 'refunded'.
        # If it fails, payment stays 'refund_pending' — visible for manual follow-up.
        payment.status = "refund_pending"
        payment.razorpay_payment_id = body.razorpay_payment_id
        payment.razorpay_signature = body.razorpay_signature
        payment.metadata_ = {"refund_reason": "slot_expired"}
        await session.commit()
        try:
            razorpay_client.refund_payment(body.razorpay_payment_id, payment.amount)
            _log.info("Refund initiated for payment %s (slot expired)", body.razorpay_payment_id)
        except Exception as exc:
            _log.error("Refund failed for payment %s: %s", body.razorpay_payment_id, exc, exc_info=True)
        raise HTTPException(
            status_code=409,
            detail="slot_expired",
        )

    booking_id, slot_time, doctor_service_id = booking_row

    # Step 4 — Mark payment succeeded
    payment.status = "succeeded"
    payment.razorpay_payment_id = body.razorpay_payment_id
    payment.razorpay_signature = body.razorpay_signature
    payment.updated_at = now

    # Fetch doctor name for response (within same session before commit)
    ds_result = await session.execute(
        select(DoctorService).where(DoctorService.id == doctor_service_id)
    )
    ds = ds_result.scalar_one_or_none()
    doctor_name = ds.doctor.name if ds else ""

    await session.commit()

    # Step 5 — Schedule Calendly event creation in background
    background_tasks.add_task(_create_calendly_event, booking_id)

    return VerifyPaymentResponse(
        ok=True,
        booking_id=booking_id,
        slot_time=slot_time,
        doctor_name=doctor_name,
        calendly_invitee_uri=None,  # populated after Calendly event created
    )


async def _create_calendly_event(booking_id: str) -> None:
    """Background task — Calendly event creation after payment confirmed."""
    # TODO: implement in Calendly integration subtask
    # 1. Load booking + doctor_service + doctor.calendly_pat
    # 2. Re-verify slot still available in Calendly
    # 3. POST /scheduled_events with doctor's PAT
    # 4. UPDATE bookings SET scheduled_at, calendly_event_uri, calendly_invitee_uri
    pass


@router.post("/webhook/razorpay", status_code=200)
async def razorpay_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    raw_body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    if not razorpay_client.verify_webhook_signature(raw_body, signature):
        raise HTTPException(status_code=400, detail="invalid_webhook_signature")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid_payload")

    event = payload.get("event")

    if event == "payment.captured":
        await _handle_payment_captured(payload, background_tasks, session)
    elif event == "payment.failed":
        await _handle_payment_failed(payload, session)
    elif event == "refund.processed":
        await _handle_refund_processed(payload, session)

    return {"ok": True}


async def _handle_payment_captured(
    payload: dict, background_tasks: BackgroundTasks, session: AsyncSession
) -> None:
    entity = payload["payload"]["payment"]["entity"]
    order_id = entity["id"]         # this is actually payment_id in Razorpay's payload
    razorpay_payment_id = entity["id"]
    razorpay_order_id = entity["order_id"]

    pay_result = await session.execute(
        select(Payment).where(Payment.razorpay_order_id == razorpay_order_id)
    )
    payment = pay_result.scalar_one_or_none()
    if not payment or payment.status in ("succeeded", "refund_pending", "refunded"):
        return  # not found or already processed — idempotent no-op

    now = datetime.now(timezone.utc)

    # Atomic slot confirm — same guard as /verify
    confirm_stmt = (
        update(Booking)
        .where(
            Booking.id == payment.reference_id,
            Booking.status == "pending_payment",
            Booking.slot_expires_at > now,
        )
        .values(status="confirmed", payment_id=payment.id, updated_at=now)
        .returning(Booking.id, Booking.slot_time, Booking.doctor_service_id)
    )
    booking_row = (await session.execute(confirm_stmt)).fetchone()

    if booking_row is None:
        # Slot expired — mark refund_pending, then initiate with Razorpay
        payment.status = "refund_pending"
        payment.razorpay_payment_id = razorpay_payment_id
        payment.metadata_ = {"refund_reason": "slot_expired"}
        await session.commit()
        try:
            razorpay_client.refund_payment(razorpay_payment_id, payment.amount)
        except Exception:
            pass
        return

    booking_id, slot_time, doctor_service_id = booking_row

    payment.status = "succeeded"
    payment.razorpay_payment_id = razorpay_payment_id
    payment.updated_at = now
    await session.commit()

    await ws_manager.broadcast(doctor_service_id, slot_time.isoformat(), "booked")
    background_tasks.add_task(_create_calendly_event, booking_id)


async def _handle_payment_failed(payload: dict, session: AsyncSession) -> None:
    entity = payload["payload"]["payment"]["entity"]
    razorpay_order_id = entity["order_id"]

    pay_result = await session.execute(
        select(Payment).where(Payment.razorpay_order_id == razorpay_order_id)
    )
    payment = pay_result.scalar_one_or_none()
    if not payment or payment.status in ("succeeded", "failed", "refund_pending", "refunded"):
        return

    now = datetime.now(timezone.utc)
    payment.status = "failed"
    payment.metadata_ = {
        "error_code": entity.get("error_code"),
        "error_description": entity.get("error_description"),
    }
    payment.updated_at = now

    await session.execute(
        update(Booking)
        .where(Booking.id == payment.reference_id, Booking.status == "pending_payment")
        .values(status="cancelled", updated_at=now)
        .returning(Booking.slot_time, Booking.doctor_service_id)
    )

    booking_result = await session.execute(
        select(Booking.slot_time, Booking.doctor_service_id).where(
            Booking.id == payment.reference_id
        )
    )
    booking_row = booking_result.fetchone()
    await session.commit()

    if booking_row:
        await ws_manager.broadcast(
            booking_row.doctor_service_id,
            booking_row.slot_time.isoformat(),
            "available",
        )


async def _handle_refund_processed(payload: dict, session: AsyncSession) -> None:
    entity = payload["payload"]["refund"]["entity"]
    razorpay_payment_id = entity["payment_id"]

    pay_result = await session.execute(
        select(Payment).where(Payment.razorpay_payment_id == razorpay_payment_id)
    )
    payment = pay_result.scalar_one_or_none()
    if not payment or payment.status == "refunded":
        return

    # Transitions refund_pending → refunded (or any other status that somehow
    # ended up with a Razorpay refund we weren't expecting)
    payment.status = "refunded"
    payment.updated_at = datetime.now(timezone.utc)
    await session.commit()
