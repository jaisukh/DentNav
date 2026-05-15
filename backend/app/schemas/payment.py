from datetime import datetime

from pydantic import BaseModel


class CreateOrderRequest(BaseModel):
    doctor_service_id: str
    slot_time: datetime


class CreateOrderResponse(BaseModel):
    order_id: str
    amount: int
    currency: str
    booking_id: str
    expires_at: datetime


class VerifyPaymentRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str


class VerifyPaymentResponse(BaseModel):
    ok: bool
    booking_id: str
    slot_time: datetime
    doctor_name: str
    calendly_invitee_uri: str | None = None
