from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_session
from app.services.auth_google import (
    build_google_oauth_url,
    exchange_google_code_for_token,
    fetch_google_email,
    upsert_google_user,
)

router = APIRouter(prefix="/auth/google", tags=["auth"])

_oauth_missing = (
    "Google OAuth is not configured. Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, "
    "and GOOGLE_REDIRECT_URI."
)


@router.get("/login")
async def google_login():
    if not settings.has_google_oauth_config:
        raise HTTPException(status_code=500, detail=_oauth_missing)
    return RedirectResponse(url=build_google_oauth_url())


@router.get("/callback")
async def google_callback(
    session: Annotated[AsyncSession, Depends(get_session)],
    code: Annotated[str | None, Query()] = None,
):
    if not code:
        raise HTTPException(status_code=400, detail="Missing OAuth code")

    if not settings.has_google_oauth_config:
        raise HTTPException(status_code=500, detail=_oauth_missing)
    try:
        token = await exchange_google_code_for_token(code)
        email = await fetch_google_email(token)
        await upsert_google_user(session, email, token)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OAuth callback failed: {exc}") from exc
    return RedirectResponse(url=f"{settings.frontend_base_url}/home")
