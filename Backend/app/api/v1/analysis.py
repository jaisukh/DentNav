from fastapi import APIRouter

from app.services.analysis import load_analysis_mock

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("")
async def get_analysis():
    return load_analysis_mock()


@router.post("")
async def post_analysis():
    # Placeholder for future LLM call; contract stays stable.
    return load_analysis_mock()
