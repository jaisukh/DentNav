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


def _readiness_overall(llm_result: dict[str, Any]) -> int:
    readiness = llm_result.get("readinessScore") or {}
    if isinstance(readiness, dict):
        overall = readiness.get("overall")
        if isinstance(overall, (int, float)):
            return int(max(0, min(100, round(overall))))
    return 0


async def create_analysis(
    session: AsyncSession,
    *,
    answers: dict[str, Any],
    llm_result: dict[str, Any],
    user_id: str | None = None,
) -> Analysis:
    """Insert a new analysis row and return it."""
    analysis = Analysis(
        id=str(uuid.uuid4()),
        user_id=user_id,
        performance=_readiness_overall(llm_result),
        answers=answers,
        llm_result=llm_result,
    )
    session.add(analysis)
    if user_id is not None:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user is not None:
            user.has_filled_questionnaire = True
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
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user is not None:
            user.has_filled_questionnaire = True
        await session.commit()
        await session.refresh(analysis)
    return analysis


def build_preview(analysis: Analysis) -> dict[str, Any]:
    """
    Return the safe-to-send preview slice. Anything not in this dict is server-
    only until the user signs in. Specifically EXCLUDES:
      pathwayRecommendation, mainRisks, next90DaysPlan, next12To18Months,
      dentnavServices, applicationTimeline, mythWarnings, statePlanning,
      expertConclusion, Body, executiveSummary, sections, actionPlan.
    """
    llm_result = analysis.llm_result if isinstance(analysis.llm_result, dict) else {}
    readiness = llm_result.get("readinessScore") or {}
    profile = llm_result.get("profileSnapshot") or {}

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
            "country": profile.get("country", ""),
            "degree": profile.get("degree", ""),
            "clinicalExperience": profile.get("clinicalExperience", ""),
        }

    return {
        "analysisId": analysis.id,
        "performance": analysis.performance,
        "readinessScore": readiness_safe,
        "profileSnapshot": profile_safe,
    }
