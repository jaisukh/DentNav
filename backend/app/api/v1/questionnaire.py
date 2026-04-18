from fastapi import APIRouter, HTTPException

from app.services.questionnaire_load import load_questionnaire_document

router = APIRouter(prefix="/questionnaire", tags=["questionnaire"])


@router.get("")
async def get_questionnaire():
    try:
        doc = await load_questionnaire_document()
        return doc.model_dump(mode="json")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to load questionnaire: {exc}") from exc
