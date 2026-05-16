export type ProfileSnapshot = {
  country: string;
  degree: string;
  clinicalExperience: string;
  targetProgram?: string;
  programIntentBadge?: string;
  entryMode?: string;
  preferredStates?: string[];
  visaStatus?: string;
  mastersInterest?: string;
  loanCosigner?: string;
  inbdeStatus?: string;
  toeflScore?: string;
  toeflLegacyEquivalent120?: string;
  targetCycle?: string;
};

export type ReadinessDimensionFull = {
  name: string;
  score: number;
  status: string;
  statusColor?: string;
};

export type ReadinessScoreFull = {
  overall: number;
  status: string;
  dimensions: ReadinessDimensionFull[];
  strengths: string[];
  gaps: string[];
};

export type RankedPathway = {
  rank: number;
  rankLabel: string;
  pathTitle: string;
  fitSummary: string;
  applicationPortal: string;
  requirementsStillNeeded: string[];
  blockers: string[];
  realityCheck: string;
  bestUseCase: string;
  isPrimary: boolean;
};

export type PathwayRecommendation = {
  primaryPathway: string;
  bestPathwayForYou: string;
  verdict: string;
  decisionNote?: string;
  secondaryStrategy?: string;
  applicationPortal: string;
  whyThisFits: string[];
  flipConditions: string[];
  whyNotAlternatives: string[];
  rankedPathways: RankedPathway[];
};

export type MainRisk = {
  issue: string;
  impact: string;
  impactColor: string;
  note: string;
  evidenceBasis: string;
  assessmentType: string;
};

export type DentnavService = {
  service: string;
  reason: string;
  timing: string;
};

export type DentnavServices = {
  neededNow: DentnavService[];
  neededLater: DentnavService[];
};

export type TimelineMilestone = {
  period: string;
  periodColor: string;
  milestone: string;
  detail: string;
};

export type MythWarning = {
  myth: string;
  fact: string;
};

export type StateInfo = {
  name: string;
  notes: string;
  competitiveness: string;
  licenseRoute: string;
  examExpectation: string;
  visaSponsorshipReality: string;
  timelineHint: string;
  priorityActions: string[];
  riskFlags: string[];
};

export type StatePlanning = {
  note: string;
  states: StateInfo[];
};

export type AnalysisFullPayload = {
  responseSchemaVersion?: string;
  Country?: string;
  degree?: string;
  yearsOfExp?: string;
  Performance?: number;
  profileSnapshot: ProfileSnapshot;
  readinessScore: ReadinessScoreFull;
  pathwayRecommendation: PathwayRecommendation;
  mainRisks: MainRisk[];
  next90DaysPlan: string[];
  next12To18Months: string[];
  dentnavServices: DentnavServices;
  applicationTimeline: TimelineMilestone[];
  mythWarnings: MythWarning[];
  statePlanning: StatePlanning;
  statePlanningNote?: string;
  expertConclusion: string;
};
