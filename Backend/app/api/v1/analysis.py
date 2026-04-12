from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.analysis import generate_analysis_from_answers, load_analysis_mock

router = APIRouter(prefix="/analysis", tags=["analysis"])


class AnalysisRequest(BaseModel):
    answers: Dict[str, Any] = Field(default_factory=dict)


@router.get("")
async def get_analysis():
    # GET is used as refresh fallback from frontend. Avoid calling LLM with an empty profile.
    return load_analysis_mock()


@router.post("")
async def post_analysis(body: AnalysisRequest):
    try:
        return await generate_analysis_from_answers(body.answers)
    except Exception as exc:  # noqa: BLE001 - API boundary
        raise HTTPException(status_code=502, detail=f"Failed to generate analysis: {exc}") from exc
