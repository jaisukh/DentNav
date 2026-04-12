from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.config import settings
from app.services.auth import (
    build_google_oauth_url,
    exchange_google_code_for_token,
    fetch_google_email,
    upsert_google_user,
)

router = APIRouter(prefix="/auth/google", tags=["auth"])


@router.get("/login")
async def google_login():
    if not settings.has_google_oauth_config:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth is not configured. Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI.",
        )
    return RedirectResponse(url=build_google_oauth_url())


@router.get("/callback")
async def google_callback(code: str = ""):
    if not code:
        raise HTTPException(status_code=400, detail="Missing OAuth code")

    if not settings.has_google_oauth_config:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth is not configured. Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI.",
        )
    try:
        token = await exchange_google_code_for_token(code)
        email = await fetch_google_email(token)
        await upsert_google_user(email, token)
    except Exception as exc:  # noqa: BLE001 - API boundary
        raise HTTPException(status_code=502, detail=f"OAuth callback failed: {exc}") from exc
    return RedirectResponse(url=f"{settings.frontend_base_url}/home")
