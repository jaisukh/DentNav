from __future__ import annotations

from dataclasses import dataclass

from app.schemas.questionnaire import (
    DropdownQuestion,
    MultiSelectQuestion,
    QuestionnaireDocument,
    RadioQuestion,
    SearchableDropdownQuestion,
    TextareaQuestion,
)


@dataclass
class AnswerValidationError:
    loc: tuple[str, ...]
    msg: str


AnswerMap = dict[str, str | list[str]]


def _sorted_questions(doc: QuestionnaireDocument):
    return sorted(doc.questions, key=lambda q: q.order)


def _is_empty(value: str | list[str] | None) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    return len(value) == 0


def _parent_country(q: DropdownQuestion, answers: AnswerMap) -> str:
    if not q.dependsOn:
        return "__ok__"
    raw = answers.get(q.dependsOn.questionId)
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return ""


def is_question_disabled(q: object, answers: AnswerMap) -> bool:
    if isinstance(q, DropdownQuestion) and q.dependsOn:
        return _parent_country(q, answers) == ""
    return False


def resolve_question_options(
    doc: QuestionnaireDocument, q: object, answers: AnswerMap
) -> list[str]:
    if isinstance(q, SearchableDropdownQuestion):
        if q.optionsFrom == "keys:degreesByCountry":
            return sorted(
                doc.degreesByCountry.keys(),
                key=lambda a: a.casefold(),
            )
        return []
    if isinstance(q, DropdownQuestion):
        if q.options:
            return list(q.options)
        if q.dependsOn:
            country = answers.get(q.dependsOn.questionId)
            if isinstance(country, str) and country.strip():
                return list(doc.degreesByCountry.get(country.strip(), []))
        return []
    if isinstance(q, (RadioQuestion, MultiSelectQuestion)):
        return list(q.options)
    return []


def normalize_raw_answers(raw: dict[str, object]) -> tuple[AnswerMap, list[AnswerValidationError]]:
    errors: list[AnswerValidationError] = []
    out: AnswerMap = {}
    for key, value in raw.items():
        if value is None:
            errors.append(AnswerValidationError(loc=("answers", key), msg="value cannot be null"))
            continue
        if isinstance(value, str):
            out[key] = value
        elif isinstance(value, list):
            parts: list[str] = []
            for i, item in enumerate(value):
                if not isinstance(item, str):
                    errors.append(
                        AnswerValidationError(
                            loc=("answers", key, str(i)),
                            msg="each selection must be a string",
                        )
                    )
                    break
                parts.append(item)
            else:
                out[key] = parts
        else:
            errors.append(
                AnswerValidationError(
                    loc=("answers", key),
                    msg="value must be a string or array of strings",
                )
            )
    return out, errors


def validate_answers(
    doc: QuestionnaireDocument, raw_answers: dict[str, object]
) -> tuple[AnswerMap, list[AnswerValidationError]]:
    answers, errors = normalize_raw_answers(raw_answers)
    known_ids = {q.id for q in doc.questions}

    for key in answers:
        if key not in known_ids:
            errors.append(
                AnswerValidationError(
                    loc=("answers", key),
                    msg=f"unknown question id {key!r}",
                )
            )

    for q in _sorted_questions(doc):
        qid = q.id
        if is_question_disabled(q, answers):
            if qid in answers and not _is_empty(answers[qid]):
                errors.append(
                    AnswerValidationError(
                        loc=("answers", qid),
                        msg="cannot answer this question before the dependent question is answered",
                    )
                )
            continue

        if isinstance(q, MultiSelectQuestion):
            if qid not in answers:
                errors.append(
                    AnswerValidationError(
                        loc=("answers", qid),
                        msg="required answer missing",
                    )
                )
                continue
            val = answers[qid]
        elif qid not in answers or _is_empty(answers[qid]):
            errors.append(
                AnswerValidationError(
                    loc=("answers", qid),
                    msg="required answer missing",
                )
            )
            continue
        else:
            val = answers[qid]

        if isinstance(q, TextareaQuestion):
            if not isinstance(val, str):
                errors.append(
                    AnswerValidationError(
                        loc=("answers", qid),
                        msg="expected a string",
                    )
                )
            continue

        opts = resolve_question_options(doc, q, answers)

        if isinstance(q, SearchableDropdownQuestion):
            if not isinstance(val, str):
                errors.append(
                    AnswerValidationError(
                        loc=("answers", qid),
                        msg="expected a string",
                    )
                )
            elif val.strip() not in doc.degreesByCountry:
                errors.append(
                    AnswerValidationError(
                        loc=("answers", qid),
                        msg="country is not in the supported list for this questionnaire",
                    )
                )

        elif isinstance(q, DropdownQuestion):
            if not isinstance(val, str):
                errors.append(
                    AnswerValidationError(
                        loc=("answers", qid),
                        msg="expected a string",
                    )
                )
            elif val not in opts:
                errors.append(
                    AnswerValidationError(
                        loc=("answers", qid),
                        msg="value is not an allowed option",
                    )
                )

        elif isinstance(q, RadioQuestion):
            if not isinstance(val, str):
                errors.append(
                    AnswerValidationError(
                        loc=("answers", qid),
                        msg="expected a string",
                    )
                )
            elif val not in opts:
                errors.append(
                    AnswerValidationError(
                        loc=("answers", qid),
                        msg="value is not an allowed option",
                    )
                )

        elif isinstance(q, MultiSelectQuestion):
            if not isinstance(val, list):
                errors.append(
                    AnswerValidationError(
                        loc=("answers", qid),
                        msg="expected an array of strings",
                    )
                )
            else:
                n = len(val)
                if q.minSelections is not None and n < q.minSelections:
                    errors.append(
                        AnswerValidationError(
                            loc=("answers", qid),
                            msg=f"select at least {q.minSelections} option(s)",
                        )
                    )
                if q.maxSelections is not None and n > q.maxSelections:
                    errors.append(
                        AnswerValidationError(
                            loc=("answers", qid),
                            msg=f"select at most {q.maxSelections} option(s)",
                        )
                    )
                bad_choice = [x for x in val if x not in opts]
                if bad_choice:
                    errors.append(
                        AnswerValidationError(
                            loc=("answers", qid),
                            msg=f"invalid selections: {bad_choice!r}",
                        )
                    )

    return answers, errors
