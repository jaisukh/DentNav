from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class QuestionnaireMeta(BaseModel):
    title: str
    description: str


class QuestionDependsOn(BaseModel):
    questionId: str
    optionsFrom: str


class QuestionBase(BaseModel):
    id: str
    order: int
    label: str
    description: str | None = None


class TextareaQuestion(QuestionBase):
    type: Literal["textarea"] = "textarea"
    placeholder: str | None = None
    rows: int | None = None


class SearchableDropdownQuestion(QuestionBase):
    type: Literal["searchableDropdown"] = "searchableDropdown"
    placeholder: str | None = None
    optionsFrom: str


class DropdownQuestion(QuestionBase):
    type: Literal["dropdown"] = "dropdown"
    placeholder: str | None = None
    options: list[str] | None = None
    dependsOn: QuestionDependsOn | None = None


class RadioQuestion(QuestionBase):
    type: Literal["radio"] = "radio"
    options: list[str]


class MultiSelectQuestion(QuestionBase):
    type: Literal["multiSelect"] = "multiSelect"
    placeholder: str | None = None
    options: list[str]
    minSelections: int | None = None
    maxSelections: int | None = None


Question = Annotated[
    TextareaQuestion
    | SearchableDropdownQuestion
    | DropdownQuestion
    | RadioQuestion
    | MultiSelectQuestion,
    Field(discriminator="type"),
]


class QuestionnaireDocument(BaseModel):
    version: str
    lastUpdated: str
    meta: QuestionnaireMeta
    degreesByCountry: dict[str, list[str]]
    questions: list[Question]


AnswerPrimitive = str | list[str]
