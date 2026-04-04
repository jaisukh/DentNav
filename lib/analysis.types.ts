/** Mock / future LLM payload for the gated analysis results page. */
export type AnalysisResultPayload = {
  Country: string;
  degree: string;
  yearsOfExp: string;
  /** Readiness score 0–100 for the circular gauge. */
  Performance: number;
  /** Visible chip label next to blurred tags (e.g. AI Insight). */
  ClearTag: string;
  /** Placeholder chips shown blurred / locked in the summary row. */
  Blurtag1: string;
  Blurtag2: string;
};
