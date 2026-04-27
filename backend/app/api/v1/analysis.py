from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.analysis import (
    AnalysisAccessStatusResponse,
    AnalysisPreviewResponse,
    AnalysisRequest,
)
from app.services.analysis import generate_analysis_from_answers, load_analysis_mock
from app.services.analysis_store import (
    build_preview,
    create_analysis,
    delete_stale_unclaimed_for_double_submit,
    get_analysis,
    get_latest_analysis_for_user,
)
from app.services.user_store import get_user_by_id
from app.services.answers_validate import validate_answers
from app.services.questionnaire_load import load_questionnaire_document
from app.services.session import verify_session_token

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("")
async def get_analysis_mock() -> dict[str, Any]:
    """
    Legacy GET fallback. Returns the bundled mock; never includes a real
    analysisId, so the gated `/full` route cannot be unlocked from here.
    """
    return load_analysis_mock()


@router.post("", response_model=AnalysisPreviewResponse)
async def post_analysis(
    request: Request,
    body: AnalysisRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AnalysisPreviewResponse:
    try:
        doc = await load_questionnaire_document()
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Failed to load questionnaire: {exc}"
        ) from exc

    answers, errors = validate_answers(doc, body.answers)
    if errors:
        raise HTTPException(
            status_code=422,
            detail=[{"loc": list(e.loc), "msg": e.msg} for e in errors],
        )

    try:
        full_payload = await generate_analysis_from_answers(answers)
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Failed to generate analysis: {exc}"
        ) from exc

    user_id = _current_user_id(request)
    analysis = await create_analysis(
        session,
        answers=dict(answers),
        payload=full_payload,
        user_id=user_id,
    )
    return AnalysisPreviewResponse.model_validate(build_preview(analysis))


@router.get("/access-status", response_model=AnalysisAccessStatusResponse)
async def get_analysis_access_status(
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
    local_analysis_id: Annotated[str | None, Query()] = None,
) -> AnalysisAccessStatusResponse:
    user_id = _current_user_id(request)
    if not user_id:
        return AnalysisAccessStatusResponse(signedIn=False)

    user = await get_user_by_id(session, user_id)
    if user is None:
        return AnalysisAccessStatusResponse(signedIn=False)

    if await delete_stale_unclaimed_for_double_submit(
        session, user_id, local_analysis_id
    ):
        response.headers["X-Removed-Stale-Questionnaire"] = "1"

    # `delete_stale_unclaimed_for_double_submit` only deletes Analysis rows;
    # `user` is still valid here (commit happened on the `analyses` table).
    analysis = await get_latest_analysis_for_user(session, user_id)
    # `user.has_filled` is authoritative; `analysis is not None` covers legacy rows
    # if the flag ever drifted.
    has_answered = user.has_filled or (analysis is not None)
    if analysis is None:
        return AnalysisAccessStatusResponse(
            signedIn=True,
            hasAnsweredQuestionnaire=has_answered,
            hasPaid=False,
            latestAnalysisId=None,
        )

    return AnalysisAccessStatusResponse(
        signedIn=True,
        hasAnsweredQuestionnaire=has_answered,
        hasPaid=analysis.paid,
        latestAnalysisId=analysis.id,
    )


@router.get("/me/preview", response_model=AnalysisPreviewResponse)
async def get_my_preview(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AnalysisPreviewResponse:
    """
    Returns the preview slice for the signed-in user's latest claimed analysis.
    Unlike `/{id}/full`, this is *not* gated on `paid`, because the preview
    slice is the same data the unpaid frontend already saw at submit time.
    """
    user_id = _current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Sign in required")
    analysis = await get_latest_analysis_for_user(session, user_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="No analysis on file")
    return AnalysisPreviewResponse.model_validate(build_preview(analysis))


@router.get("/me/answers")
async def get_my_answers(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, Any]:
    """
    Returns the raw questionnaire answers for the user's latest analysis,
    paired with the questionnaire document so the client can render
    Q -> A list without re-fetching the questionnaire.
    """
    user_id = _current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Sign in required")
    analysis = await get_latest_analysis_for_user(session, user_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="No analysis on file")
    try:
        doc = await load_questionnaire_document()
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Failed to load questionnaire: {exc}"
        ) from exc
    answers = analysis.answers if isinstance(analysis.answers, dict) else {}
    return {"questionnaire": doc.model_dump(mode="json"), "answers": answers}


@router.get("/{analysis_id}/full")
async def get_full_analysis(
    analysis_id: str,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, Any]:
    """
    Returns the full payload. Requires the analysis to (a) be claimed by the
    current user and (b) be marked `paid`. Auth/payment wiring is intentionally
    minimal here — sign-in & payment flow are tracked separately. Until those
    land, this endpoint is effectively locked.
    """
    analysis = await get_analysis(session, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    user_id = _current_user_id(request)
    if analysis.user_id is None or analysis.user_id != user_id:
        raise HTTPException(status_code=403, detail="Sign in to access this analysis")
    if not analysis.paid:
        raise HTTPException(status_code=402, detail="Payment required to unlock full roadmap")

    return analysis.payload


def _current_user_id(request: Request) -> str | None:
    token = request.cookies.get("dentnav_user_id")
    if not token:
        return None
    return verify_session_token(token)
