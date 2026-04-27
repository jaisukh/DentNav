"""
Persistence helpers for the `analyses` table.

The full LLM payload is the source of truth and is only released to the client
through the gated `/api/v1/analysis/{id}/full` endpoint after sign-in + payment.
The questionnaire submit endpoint stores the row and returns only a preview
slice so the unpaid frontend (and anyone watching the network tab) can never
see the full body / pathway / risks / timeline.
"""
import re
import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis
from app.models.user import User

_ANALYSIS_UUID = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _profile_field(payload: dict[str, Any], key: str, fallback: str = "") -> str:
    profile = payload.get("profileSnapshot") or {}
    if isinstance(profile, dict):
        value = profile.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _readiness_overall(payload: dict[str, Any]) -> int:
    readiness = payload.get("readinessScore") or {}
    if isinstance(readiness, dict):
        overall = readiness.get("overall")
        if isinstance(overall, (int, float)):
            return int(max(0, min(100, round(overall))))
    return 0


async def create_analysis(
    session: AsyncSession,
    *,
    answers: dict[str, Any],
    payload: dict[str, Any],
    user_id: str | None = None,
) -> Analysis:
    """Insert a new analysis row and return it."""
    analysis = Analysis(
        id=str(uuid.uuid4()),
        user_id=user_id,
        paid=False,
        country=_profile_field(payload, "country"),
        degree=_profile_field(payload, "degree"),
        years_of_exp=_profile_field(payload, "clinicalExperience"),
        performance=_readiness_overall(payload),
        answers=answers,
        payload=payload,
    )
    session.add(analysis)
    if user_id is not None:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is not None:
            user.has_filled = True
    await session.commit()
    await session.refresh(analysis)
    return analysis


async def get_analysis(session: AsyncSession, analysis_id: str) -> Analysis | None:
    result = await session.execute(select(Analysis).where(Analysis.id == analysis_id))
    return result.scalar_one_or_none()


async def delete_stale_unclaimed_for_double_submit(
    session: AsyncSession, user_id: str, local_analysis_id: str | None
) -> bool:
    """
    When the user already has a claimed analysis but localStorage still points
    to a *second* submission (unclaimed), remove that extra row. Returns True if
    a row was deleted.

    The DELETE is a single statement that only matches rows with ``user_id IS
    NULL``. If a concurrent request (e.g. OAuth callback in another tab) claims
    the same analysis between our policy check and the delete, the row no
    longer matches and the delete is a no-op — we never remove a claimed row.
    """
    if not local_analysis_id or not _ANALYSIS_UUID.match(local_analysis_id):
        return False
    claims = await session.execute(
        select(Analysis.id).where(Analysis.user_id == user_id).limit(1)
    )
    if claims.scalar_one_or_none() is None:
        return False
    result = await session.execute(
        delete(Analysis).where(
            Analysis.id == local_analysis_id,
            Analysis.user_id.is_(None),
        )
    )
    await session.commit()
    # 0 / -1 / None: wrong id, already claimed, or already deleted
    rc = result.rowcount
    return bool(rc and rc > 0)


async def user_has_claimed_analysis(session: AsyncSession, user_id: str) -> bool:
    """True when the user already has at least one analysis row attached."""
    result = await session.execute(
        select(Analysis.id).where(Analysis.user_id == user_id).limit(1)
    )
    return result.scalar_one_or_none() is not None


async def get_latest_analysis_for_user(
    session: AsyncSession, user_id: str
) -> Analysis | None:
    result = await session.execute(
        select(Analysis)
        .where(Analysis.user_id == user_id)
        .order_by(Analysis.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def claim_analysis(
    session: AsyncSession, analysis_id: str, user_id: str
) -> Analysis | None:
    """Attach an anonymous analysis to a signed-in user. No-op if already owned."""
    analysis = await get_analysis(session, analysis_id)
    if analysis is None:
        return None
    if analysis.user_id is None:
        analysis.user_id = user_id
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is not None:
            user.has_filled = True
        await session.commit()
        await session.refresh(analysis)
    return analysis


async def mark_paid(session: AsyncSession, analysis_id: str) -> Analysis | None:
    analysis = await get_analysis(session, analysis_id)
    if analysis is None:
        return None
    if not analysis.paid:
        analysis.paid = True
        await session.commit()
        await session.refresh(analysis)
    return analysis


def build_preview(analysis: Analysis) -> dict[str, Any]:
    """
    Return the safe-to-send preview slice. Anything not in this dict is server-
    only until the user signs in + pays. Specifically EXCLUDES:
      pathwayRecommendation, mainRisks, next90DaysPlan, next12To18Months,
      dentnavServices, applicationTimeline, mythWarnings, statePlanning,
      expertConclusion, Body, executiveSummary, sections, actionPlan.
    """
    payload = analysis.payload if isinstance(analysis.payload, dict) else {}
    readiness = payload.get("readinessScore") or {}
    profile = payload.get("profileSnapshot") or {}

    readiness_safe: dict[str, Any] = {}
    if isinstance(readiness, dict):
        readiness_safe = {
            "overall": readiness.get("overall", analysis.performance),
            "status": readiness.get("status", ""),
            "dimensions": readiness.get("dimensions", []),
            "strengths": readiness.get("strengths", []),
            "gaps": readiness.get("gaps", []),
        }

    profile_safe: dict[str, Any] = {}
    if isinstance(profile, dict):
        profile_safe = {
            "country": profile.get("country", analysis.country),
            "degree": profile.get("degree", analysis.degree),
            "clinicalExperience": profile.get(
                "clinicalExperience", analysis.years_of_exp
            ),
        }

    return {
        "analysisId": analysis.id,
        "country": analysis.country or profile_safe.get("country", ""),
        "degree": analysis.degree or profile_safe.get("degree", ""),
        "yearsOfExp": analysis.years_of_exp
        or profile_safe.get("clinicalExperience", ""),
        "performance": analysis.performance,
        "readinessScore": readiness_safe,
        "profileSnapshot": profile_safe,
        "paid": analysis.paid,
    }
