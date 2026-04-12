from fastapi import APIRouter, HTTPException

from app.services.questionnaire import load_questionnaire

router = APIRouter(prefix="/questionnaire", tags=["questionnaire"])


@router.get("")
async def get_questionnaire():
    try:
        return await load_questionnaire()
    except Exception as exc:  # noqa: BLE001 - API boundary
        raise HTTPException(status_code=502, detail=f"Failed to load questionnaire: {exc}") from exc
