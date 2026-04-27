"""JWT session token and OAuth CSRF helpers."""

import secrets
from datetime import UTC, datetime, timedelta

import jwt

from app.config import settings

_ALGORITHM = "HS256"
_SESSION_MAX_AGE = timedelta(days=30)

# ---------------------------------------------------------------------------
# Session cookie
# ---------------------------------------------------------------------------


def create_session_token(user_id: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + _SESSION_MAX_AGE,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)


def verify_session_token(token: str) -> str | None:
    """Return user_id if valid, None otherwise."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[_ALGORITHM])
        return payload.get("sub")
    except (jwt.InvalidTokenError, Exception):
        return None


# ---------------------------------------------------------------------------
# OAuth CSRF nonce (double-submit cookie pattern)
# ---------------------------------------------------------------------------


def generate_csrf_nonce() -> str:
    return secrets.token_urlsafe(32)


def verify_csrf_nonce(state: str, cookie_nonce: str) -> bool:
    if not state or not cookie_nonce:
        return False
    return secrets.compare_digest(state, cookie_nonce)
