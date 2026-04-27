"""Google OAuth helpers.

Note on token persistence: we deliberately do NOT store the OAuth access token
(see migration `0003_users_names_has_filled_drop_token`). The token is only
used during the callback to read the user's profile (`given_name`,
`family_name`, `email`); after that we rely on our own signed JWT session
cookie. This means we can't call Google's `/revoke` endpoint at logout, but
Google access tokens auto-expire within ~1h and the session JWT is
invalidated by clearing the cookie, so the practical exposure is limited.
"""

import uuid
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"
GOOGLE_OAUTH_SCOPE = "openid email profile"


def build_google_oauth_url(state: str) -> str:
    """`state` is required and must be the CSRF nonce verified in the callback."""
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": GOOGLE_OAUTH_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(params)}"


async def exchange_google_code_for_token(code: str) -> str:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            GOOGLE_TOKEN_ENDPOINT,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        payload = response.json()
        access_token = payload.get("access_token", "")
        if not access_token:
            raise ValueError("Google token endpoint returned no access_token")
        return access_token


@dataclass(frozen=True, slots=True)
class GoogleUserInfo:
    email: str
    first_name: str
    last_name: str


async def fetch_google_user_info(access_token: str) -> GoogleUserInfo:
    """
    Fetches the signed-in user from Google. `given_name` and `family_name` are
    available when the token was issued with the `profile` scope (included in
    GOOGLE_OAUTH_SCOPE). Some Google accounts return only a display `name` — we
    fall back to empty strings for missing name parts; email is still required.
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            GOOGLE_USERINFO_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        payload = response.json()
        email = payload.get("email", "")
        if not email or not isinstance(email, str):
            raise ValueError("Google userinfo returned no email")

        first = payload.get("given_name")
        last = payload.get("family_name")
        if isinstance(first, str) and first.strip():
            first_name = first.strip()
        else:
            # Rare: only `name` is present; put everything in first_name
            name = payload.get("name")
            if isinstance(name, str) and name.strip():
                first_name = name.strip()
            else:
                first_name = ""
        if isinstance(last, str) and last.strip():
            last_name = last.strip()
        else:
            last_name = ""

    return GoogleUserInfo(email=email, first_name=first_name, last_name=last_name)


async def upsert_google_user(
    session: AsyncSession, info: GoogleUserInfo
) -> str:
    """Insert or update the user row for this Google account. Returns user id."""
    result = await session.execute(select(User).where(User.email == info.email))
    user = result.scalar_one_or_none()
    if user:
        user.first_name = info.first_name
        user.last_name = info.last_name
    else:
        user = User(
            id=str(uuid.uuid4()),
            email=info.email,
            first_name=info.first_name,
            last_name=info.last_name,
            has_filled=False,
        )
        session.add(user)
    await session.commit()
    await session.refresh(user)
    return user.id
