/**
 * Public preview payload returned from POST /api/v1/analysis.
 *
 * The backend intentionally only returns the readiness-score breakdown +
 * profile snapshot fields needed for the locked preview UI. The full payload
 * (pathway, risks, timeline, body, etc.) is stored server-side and is only
 * released through GET /api/v1/analysis/{id}/full after sign-in + payment.
 *
 * IMPORTANT: do not add `Body` / `pathwayRecommendation` / `mainRisks` etc
 * here. Anything declared on this type will end up in the network response
 * and defeats the gating.
 */

export type ReadinessDimension = {
  /** Display label, e.g. "Exam readiness (INBDE)". */
  name: string;
  /** 0–100. */
  score: number;
  /** Status word the LLM returned, e.g. "Strong" / "Good" / "Gap" / "Unclear". */
  status: string;
  /** Optional hint from the LLM about color bucket (green/orange/red). */
  statusColor?: string;
};

export type ReadinessScore = {
  /** Overall readiness 0–100. Same value as `Performance`. */
  overall: number;
  /** Headline label, e.g. "Promising but not application-ready yet". */
  status: string;
  dimensions: ReadinessDimension[];
  strengths: string[];
  gaps: string[];
};

export type ProfileSnapshotPreview = {
  country: string;
  degree: string;
  clinicalExperience: string;
};

export type AnalysisPreviewPayload = {
  /** Server-side id used to claim/unlock the full payload after sign-in + pay. */
  analysisId: string;
  country: string;
  degree: string;
  yearsOfExp: string;
  /** Mirror of readinessScore.overall for legacy gauge consumers. */
  performance: number;
  readinessScore: ReadinessScore;
  profileSnapshot: ProfileSnapshotPreview;
  /** True once the server has marked this analysis as paid. */
  paid: boolean;
};
