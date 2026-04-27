import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_session
from app.services.analysis_store import (
    claim_analysis,
    delete_stale_unclaimed_for_double_submit,
    user_has_claimed_analysis,
)
from app.services.auth_google import (
    build_google_oauth_url,
    exchange_google_code_for_token,
    fetch_google_user_info,
    upsert_google_user,
)
from app.services.session import (
    create_session_token,
    generate_csrf_nonce,
    verify_csrf_nonce,
)

router = APIRouter(prefix="/auth/google", tags=["auth"])

_oauth_missing = (
    "Google OAuth is not configured. Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, "
    "and GOOGLE_REDIRECT_URI."
)

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

# Short-lived cookies set on /login and consumed on /callback. Scoped to the
# callback path so they never travel with normal API requests.
_OAUTH_CALLBACK_PATH = "/api/v1/auth/google/callback"
_OAUTH_COOKIE_TTL = 300  # 5 minutes


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

    # `state` is the CSRF nonce verified in the callback (double-submit cookie).
    nonce = generate_csrf_nonce()
    response = RedirectResponse(url=build_google_oauth_url(state=nonce))
    secure, samesite = _session_cookie_kwargs()
    response.set_cookie(
        key="oauth_nonce",
        value=nonce,
        max_age=_OAUTH_COOKIE_TTL,
        httponly=True,
        samesite=samesite,
        secure=secure,
        path=_OAUTH_CALLBACK_PATH,
    )
    # The optional analysis_id rides in its own short-lived cookie so we can
    # reclaim a freshly submitted anonymous analysis row right after sign-in.
    aid = _sanitize_analysis_id(analysis_id)
    if aid:
        response.set_cookie(
            key="oauth_analysis_id",
            value=aid,
            max_age=_OAUTH_COOKIE_TTL,
            httponly=True,
            samesite=samesite,
            secure=secure,
            path=_OAUTH_CALLBACK_PATH,
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
    # Google forwards `?error=access_denied` when the user cancels consent. We
    # bounce them back to /auth/login with the error visible, instead of
    # showing a raw 400 from this endpoint.
    if error:
        return RedirectResponse(
            url=f"{settings.frontend_base_url}/auth/login?error={error}"
        )
    if not code:
        raise HTTPException(status_code=400, detail="Missing OAuth code")
    if not state:
        raise HTTPException(status_code=400, detail="Missing OAuth state")
    if not settings.has_google_oauth_config:
        raise HTTPException(status_code=500, detail=_oauth_missing)

    # CSRF: the `state` query param must match the cookie we set on /login.
    cookie_nonce = request.cookies.get("oauth_nonce", "")
    if not verify_csrf_nonce(state, cookie_nonce):
        raise HTTPException(status_code=403, detail="Invalid or expired OAuth state")

    try:
        access_token = await exchange_google_code_for_token(code)
        user_info = await fetch_google_user_info(access_token)
        user_id = await upsert_google_user(session, user_info)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OAuth callback failed: {exc}") from exc

    # Optional anonymous-analysis reclaim. The id comes from the dedicated
    # cookie (NOT from `state` — `state` is now exclusively the CSRF nonce).
    analysis_id = _sanitize_analysis_id(request.cookies.get("oauth_analysis_id"))
    reclaimed_existing = False
    if analysis_id:
        if await user_has_claimed_analysis(session, user_id):
            # Existing user re-submitted while signed out; drop the new
            # unclaimed row instead of stacking it on top of their existing
            # claimed analysis. The /landing page surfaces a toast for this.
            removed = await delete_stale_unclaimed_for_double_submit(
                session, user_id, analysis_id
            )
            reclaimed_existing = removed
        else:
            await claim_analysis(session, analysis_id, user_id)

    target = f"{settings.frontend_base_url}/landing"
    if reclaimed_existing:
        target = f"{target}?reclaimed_existing=1"
    response = RedirectResponse(url=target)
    secure, samesite = _session_cookie_kwargs()

    # Signed JWT, NOT a raw UUID, so cookie-injection alone cannot impersonate
    # any user. The cookie is httpOnly + SameSite, refreshed for 30 days.
    response.set_cookie(
        key="dentnav_user_id",
        value=create_session_token(user_id),
        max_age=60 * 60 * 24 * 30,
        httponly=True,
        samesite=samesite,
        secure=secure,
    )
    # Burn the short-lived OAuth cookies so a replay can't reuse the same nonce.
    response.delete_cookie(
        key="oauth_nonce",
        httponly=True,
        samesite=samesite,
        secure=secure,
        path=_OAUTH_CALLBACK_PATH,
    )
    response.delete_cookie(
        key="oauth_analysis_id",
        httponly=True,
        samesite=samesite,
        secure=secure,
        path=_OAUTH_CALLBACK_PATH,
    )
    return response


@router.post("/logout")
async def google_logout(response: Response) -> dict[str, bool]:
    # NOTE: we deliberately do not call Google's /revoke here because we no
    # longer persist the access token (see migration 0003). The session JWT
    # cookie is the only client-visible token and we clear it below; Google
    # access tokens auto-expire within ~1h.
    secure, samesite = _session_cookie_kwargs()
    response.delete_cookie(
        key="dentnav_user_id",
        httponly=True,
        samesite=samesite,
        secure=secure,
    )
    return {"ok": True}
