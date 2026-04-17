import json
from pathlib import Path

import pytest
from app.schemas.questionnaire import QuestionnaireDocument
from app.services.answers_validate import validate_answers


@pytest.fixture
def doc() -> QuestionnaireDocument:
    p = Path(__file__).resolve().parents[1] / "data" / "questionnaire.v1.json"
    return QuestionnaireDocument.model_validate(json.loads(p.read_text(encoding="utf-8")))


def test_validate_full_profile_ok(doc: QuestionnaireDocument) -> None:
    answers = {
        "q1-degree-country": "India",
        "q1b-degree-type": "BDS",
        "q2-target-program": "DDS / DMD",
        "q3-practice-states": ["California", "Texas"],
        "q4-visa": "F1",
        "q5-masters-vs-home": "Apply to dental schools from home country",
        "q6-loan-cosigner": "No",
        "q7-clinical-years": "5-6",
        "q8-inbde": "Yes",
        "q9-toefl": "5",
        "q10-start-cycle": "2027",
    }
    out, errors = validate_answers(doc, answers)
    assert not errors
    assert out["q1-degree-country"] == "India"


def test_unknown_question_id(doc: QuestionnaireDocument) -> None:
    _, errors = validate_answers(doc, {"q1-degree-country": "India", "bad-id": "x"})
    assert any("unknown question" in e.msg for e in errors)


def test_dependent_before_parent(doc: QuestionnaireDocument) -> None:
    _, errors = validate_answers(
        doc,
        {"q1b-degree-type": "BDS"},
    )
    assert any("dependent" in e.msg for e in errors)
