from fastapi import APIRouter, HTTPException

from app.schemas.analysis import AnalysisRequest
from app.services.analysis import generate_analysis_from_answers, load_analysis_mock
from app.services.answers_validate import validate_answers
from app.services.questionnaire_load import load_questionnaire_document

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("")
async def get_analysis():
    return load_analysis_mock()


@router.post("")
async def post_analysis(body: AnalysisRequest):
    try:
        doc = await load_questionnaire_document()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to load questionnaire: {exc}") from exc

    _answers, errors = validate_answers(doc, body.answers)
    if errors:
        raise HTTPException(
            status_code=422,
            detail=[{"loc": list(e.loc), "msg": e.msg} for e in errors],
        )

    try:
        return await generate_analysis_from_answers(_answers)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to generate analysis: {exc}") from exc
