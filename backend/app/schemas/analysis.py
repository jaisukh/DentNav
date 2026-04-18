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
    programIntentBadge: str = ""
    entryMode: str = ""
    preferredStates: list[str] = Field(default_factory=list)
    visaStatus: str = ""
    mastersInterest: str = ""
    loanCosigner: str = ""
    inbdeStatus: str = ""
    toeflScore: str = ""
    toeflLegacyEquivalent120: str = ""
    targetCycle: str = ""


class ReadinessDimension(BaseModel):
    name: str = ""
    score: int = Field(ge=0, le=100, default=0)
    status: str = ""
    statusColor: str = ""


class ReadinessScore(BaseModel):
    overall: int = Field(ge=0, le=100)
    status: str = ""
    dimensions: list[ReadinessDimension] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class RankedPathway(BaseModel):
    rank: int = 0
    rankLabel: str = ""
    pathTitle: str = ""
    fitSummary: str = ""
    applicationPortal: str = ""
    requirementsStillNeeded: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    realityCheck: str = ""
    bestUseCase: str = ""
    isPrimary: bool = False


class PathwayRecommendation(BaseModel):
    primaryPathway: str = ""
    bestPathwayForYou: str = ""
    verdict: str = ""
    decisionNote: str = ""
    secondaryStrategy: str = ""
    applicationPortal: str = ""
    whyThisFits: list[str] = Field(default_factory=list)
    flipConditions: list[str] = Field(default_factory=list)
    whyNotAlternatives: list[str] = Field(default_factory=list)
    rankedPathways: list[RankedPathway] = Field(default_factory=list)


class RiskItem(BaseModel):
    issue: str = ""
    impact: str = ""
    impactColor: str = ""
    note: str = ""
    evidenceBasis: str = ""
    assessmentType: str = ""


class ServiceNeedItem(BaseModel):
    service: str = ""
    reason: str = ""
    timing: str = ""


class DentnavServices(BaseModel):
    neededNow: list[ServiceNeedItem] = Field(default_factory=list)
    neededLater: list[ServiceNeedItem] = Field(default_factory=list)


class TimelineMilestone(BaseModel):
    period: str = ""
    periodColor: str = ""
    milestone: str = ""
    detail: str = ""


class MythWarningItem(BaseModel):
    myth: str = ""
    fact: str = ""


class StatePlanningState(BaseModel):
    name: str = ""
    notes: str = ""
    competitiveness: str = ""


class StatePlanning(BaseModel):
    note: str = ""
    states: list[StatePlanningState] = Field(default_factory=list)


class AnalysisResultPayload(BaseModel):
    responseSchemaVersion: str = ""
    profileSnapshot: ProfileSnapshot = Field(default_factory=ProfileSnapshot)
    readinessScore: ReadinessScore = Field(default_factory=lambda: ReadinessScore(overall=0))
    pathwayRecommendation: PathwayRecommendation = Field(default_factory=PathwayRecommendation)
    mainRisks: list[RiskItem] = Field(default_factory=list)
    next90DaysPlan: list[str] = Field(default_factory=list)
    next12To18Months: list[str] = Field(default_factory=list)
    dentnavServices: DentnavServices = Field(default_factory=DentnavServices)
    applicationTimeline: list[TimelineMilestone] = Field(default_factory=list)
    mythWarnings: list[MythWarningItem] = Field(default_factory=list)
    statePlanning: StatePlanning = Field(default_factory=StatePlanning)
    statePlanningNote: str = ""
    expertConclusion: str = ""

    # Backward-compatible fields
    Country: str = ""
    degree: str = ""
    yearsOfExp: str = ""
    Performance: int = Field(ge=0, le=100, default=50)
    executiveSummary: str = ""
    sections: list[AnalysisSection] = Field(default_factory=list)
    actionPlan: list[ActionItem] = Field(default_factory=list)
    keyInsight: str = ""
    Body: list[str] | str = Field(default_factory=list)

    @field_validator("Body", mode="before")
    @classmethod
    def _body_to_list_friendly(cls, v: Any) -> Any:
        return v
