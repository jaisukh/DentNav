from typing import Any

from pydantic import BaseModel, Field, field_validator


class AnalysisRequest(BaseModel):
    answers: dict[str, Any] = Field(default_factory=dict)


class AnalysisSection(BaseModel):
    heading: str
    body: list[str]


class ActionItem(BaseModel):
    action: str
    timeline: str
    why: str


class ProfileSnapshot(BaseModel):
    country: str = ""
    degree: str = ""
    clinicalExperience: str = ""
    targetProgram: str = ""
    preferredStates: list[str] = Field(default_factory=list)
    visaStatus: str = ""
    mastersInterest: str = ""
    loanCosigner: str = ""
    inbdeStatus: str = ""
    toeflScore: str = ""
    toeflLegacyEquivalent120: str = ""
    targetCycle: str = ""


class ReadinessScore(BaseModel):
    overall: int = Field(ge=0, le=100)
    status: str = ""
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class PathwayRecommendation(BaseModel):
    primaryPathway: str = ""
    verdict: str = ""
    whyThisFits: list[str] = Field(default_factory=list)
    secondaryStrategy: str = ""


class RiskItem(BaseModel):
    issue: str = ""
    impact: str = ""
    note: str = ""
    evidenceBasis: str = ""
    assessmentType: str = ""


class QuestionGroundingItem(BaseModel):
    questionId: str = ""
    answer: str = ""
    pathwayInfluence: str = ""


class AnalysisResultPayload(BaseModel):
    responseSchemaVersion: str = ""
    profileSnapshot: ProfileSnapshot = Field(default_factory=ProfileSnapshot)
    readinessScore: ReadinessScore = Field(default_factory=lambda: ReadinessScore(overall=0))
    pathwayRecommendation: PathwayRecommendation = Field(default_factory=PathwayRecommendation)
    mainRisks: list[RiskItem] = Field(default_factory=list)
    next90DaysPlan: list[str] = Field(default_factory=list)
    next12To18Months: list[str] = Field(default_factory=list)
    questionnaireGrounding: list[QuestionGroundingItem] = Field(default_factory=list)
    assessmentBoundaries: list[str] = Field(default_factory=list)
    statePlanningNote: str = ""
    expertConclusion: str = ""

    # Backward-compatible fields currently still returned by service
    Country: str
    degree: str
    yearsOfExp: str
    Performance: int = Field(ge=0, le=100)
    executiveSummary: str = ""
    sections: list[AnalysisSection] = Field(default_factory=list)
    actionPlan: list[ActionItem] = Field(default_factory=list)
    keyInsight: str = ""
    Body: list[str] | str = Field(default_factory=list)

    @field_validator("Body", mode="before")
    @classmethod
    def _body_to_list_friendly(cls, v: Any) -> Any:
        return v
