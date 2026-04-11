/** Mock / future LLM payload for the gated analysis results page. */
export type AnalysisResultPayload = {
  Country: string;
  degree: string;
  yearsOfExp: string;
  /** Readiness score 0–100 for the circular gauge. */
  Performance: number;
};
