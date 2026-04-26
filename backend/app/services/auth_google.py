import uuid
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"
GOOGLE_REVOKE_ENDPOINT = "https://oauth2.googleapis.com/revoke"
GOOGLE_OAUTH_SCOPE = "openid email profile"


def build_google_oauth_url(state: str) -> str:
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


async def fetch_google_email(access_token: str) -> str:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            GOOGLE_USERINFO_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        payload = response.json()
        email = payload.get("email", "")
        if not email:
            raise ValueError("Google userinfo returned no email")
        return email


async def revoke_google_token(access_token: str) -> bool:
    """Best-effort token revocation. Returns True if Google accepted."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                GOOGLE_REVOKE_ENDPOINT,
                params={"token": access_token},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            return resp.status_code == 200
    except Exception:
        return False


async def upsert_google_user(session: AsyncSession, email: str, token: str) -> str:
    """Insert or update the user row for this Google email. Returns the user id."""
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        user.token = token
    else:
        user = User(id=str(uuid.uuid4()), email=email, token=token)
        session.add(user)
    await session.commit()
    await session.refresh(user)
    return user.id
