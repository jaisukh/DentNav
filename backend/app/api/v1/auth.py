import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_session
from app.services.analysis_store import claim_analysis
from app.services.auth_google import (
    build_google_oauth_url,
    exchange_google_code_for_token,
    fetch_google_email,
    upsert_google_user,
)
from app.services.session import create_session_token

router = APIRouter(prefix="/auth/google", tags=["auth"])

_oauth_missing = (
    "Google OAuth is not configured. Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, "
    "and GOOGLE_REDIRECT_URI."
)

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _session_cookie_kwargs() -> tuple[bool, str]:
    """HTTPS: SameSite=None+Secure so credentialed cross-origin fetch from the SPA works."""
    secure = settings.frontend_base_url.startswith("https://")
    samesite: str = "none" if secure else "lax"
    return secure, samesite


def _sanitize_analysis_id(value: str | None) -> str | None:
    if value and _UUID_RE.match(value):
        return value
    return None


@router.get("/login")
async def google_login(
    analysis_id: Annotated[str | None, Query(alias="analysis_id")] = None,
):
    if not settings.has_google_oauth_config:
        raise HTTPException(status_code=500, detail=_oauth_missing)
    # The OAuth `state` round-trips back to /callback so we can associate the
    # anonymous analysis row with the user right after sign-in.
    state = _sanitize_analysis_id(analysis_id)
    return RedirectResponse(url=build_google_oauth_url(state=state))


@router.get("/callback")
async def google_callback(
    session: Annotated[AsyncSession, Depends(get_session)],
    code: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
):
    if not code:
        raise HTTPException(status_code=400, detail="Missing OAuth code")

    if not settings.has_google_oauth_config:
        raise HTTPException(status_code=500, detail=_oauth_missing)
    try:
        token = await exchange_google_code_for_token(code)
        email = await fetch_google_email(token)
        user_id = await upsert_google_user(session, email, token)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OAuth callback failed: {exc}") from exc

    # Link the anonymous analysis (if we have one from the login redirect) to
    # this user so we can surface it after payment without asking them to
    # refill the questionnaire.
    analysis_id = _sanitize_analysis_id(state)
    if analysis_id:
        await claim_analysis(session, analysis_id, user_id)

    # Always land on the dedicated post-sign-in page. How/when to surface the
    # claimed analysis row is a separate product decision (gated by payment).
    response = RedirectResponse(url=f"{settings.frontend_base_url}/landing")
    secure, samesite = _session_cookie_kwargs()
    response.set_cookie(
        key="dentnav_user_id",
        value=create_session_token(user_id),
        max_age=60 * 60 * 24 * 30,
        httponly=True,
        samesite=samesite,
        secure=secure,
    )
    return response


@router.post("/logout")
async def google_logout(response: Response) -> dict[str, bool]:
    secure, samesite = _session_cookie_kwargs()
    response.delete_cookie(
        key="dentnav_user_id",
        httponly=True,
        samesite=samesite,
        secure=secure,
    )
    return {"ok": True}
