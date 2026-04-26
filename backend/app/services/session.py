"""JWT-based session cookie helpers."""

from datetime import UTC, datetime, timedelta

import jwt

from app.config import settings

_ALGORITHM = "HS256"
_SESSION_MAX_AGE = timedelta(days=30)


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
