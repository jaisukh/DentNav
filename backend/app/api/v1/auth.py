import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
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
from app.services.session import create_session_token, generate_csrf_nonce, verify_csrf_nonce

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
    nonce = generate_csrf_nonce()
    response = RedirectResponse(url=build_google_oauth_url(state=nonce))
    secure, samesite = _session_cookie_kwargs()
    callback_path = "/api/v1/auth/google/callback"
    response.set_cookie(
        key="oauth_nonce",
        value=nonce,
        max_age=300,
        httponly=True,
        samesite=samesite,
        secure=secure,
        path=callback_path,
    )
    aid = _sanitize_analysis_id(analysis_id)
    if aid:
        response.set_cookie(
            key="oauth_analysis_id",
            value=aid,
            max_age=300,
            httponly=True,
            samesite=samesite,
            secure=secure,
            path=callback_path,
        )
    return response


@router.get("/callback")
async def google_callback(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    code: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
    error: Annotated[str | None, Query()] = None,
):
    if error:
        return RedirectResponse(url=f"{settings.frontend_base_url}/auth/login?error={error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing OAuth code")
    if not state:
        raise HTTPException(status_code=400, detail="Missing OAuth state")
    if not settings.has_google_oauth_config:
        raise HTTPException(status_code=500, detail=_oauth_missing)

    # --- CSRF verification (must happen before anything else) ---
    cookie_nonce = request.cookies.get("oauth_nonce", "")
    if not verify_csrf_nonce(state, cookie_nonce):
        raise HTTPException(status_code=403, detail="Invalid or expired OAuth state")

    try:
        token = await exchange_google_code_for_token(code)
        email = await fetch_google_email(token)
        user_id = await upsert_google_user(session, email, token)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OAuth callback failed: {exc}") from exc

    analysis_id = _sanitize_analysis_id(request.cookies.get("oauth_analysis_id"))
    if analysis_id:
        await claim_analysis(session, analysis_id, user_id)

    response = RedirectResponse(url=f"{settings.frontend_base_url}/landing")
    secure, samesite = _session_cookie_kwargs()
    callback_path = "/api/v1/auth/google/callback"
    response.set_cookie(
        key="dentnav_user_id",
        value=create_session_token(user_id),
        max_age=60 * 60 * 24 * 30,
        httponly=True,
        samesite=samesite,
        secure=secure,
    )
    response.delete_cookie(
        key="oauth_nonce", httponly=True, samesite=samesite, secure=secure, path=callback_path,
    )
    response.delete_cookie(
        key="oauth_analysis_id",
        httponly=True,
        samesite=samesite,
        secure=secure,
        path=callback_path,
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
