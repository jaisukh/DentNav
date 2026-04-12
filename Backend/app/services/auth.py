from urllib.parse import urlencode

import httpx

from app.config import settings
from app.db import db

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"
GOOGLE_OAUTH_SCOPE = "openid email profile"


def build_google_oauth_url() -> str:
    query = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": GOOGLE_OAUTH_SCOPE,
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    return f"{GOOGLE_AUTH_ENDPOINT}?{query}"


async def exchange_google_code_for_token(code: str) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
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
    async with httpx.AsyncClient(timeout=15) as client:
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


async def upsert_google_user(email: str, token: str) -> None:
    await db.user.upsert(
        where={"email": email},
        data={
            "create": {"email": email, "token": token},
            "update": {"token": token},
        },
    )
