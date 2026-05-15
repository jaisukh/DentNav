"""Razorpay API helpers — thin wrapper around the official SDK."""

import hashlib
import hmac

import razorpay

from app.config import settings


def _client() -> razorpay.Client:
    return razorpay.Client(
        auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
    )


def create_order(amount: int, currency: str, receipt: str, notes: dict) -> dict:
    """Create a Razorpay order. amount is in minor units (paise/cents)."""
    return _client().order.create(
        {
            "amount": amount,
            "currency": currency.upper(),
            "receipt": receipt,
            "notes": notes,
        }
    )


def verify_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """HMAC-SHA256 verification of the Razorpay payment signature."""
    message = f"{order_id}|{payment_id}"
    expected = hmac.new(
        settings.razorpay_key_secret.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def verify_webhook_signature(raw_body: bytes, signature: str) -> bool:
    """HMAC-SHA256 verification of a Razorpay webhook payload against the webhook secret."""
    expected = hmac.new(
        settings.razorpay_webhook_secret.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def refund_payment(payment_id: str, amount: int) -> dict:
    return _client().payment.refund(payment_id, {"amount": amount})
