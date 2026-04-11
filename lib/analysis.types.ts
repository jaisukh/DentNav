/** Mock / future LLM payload for the gated analysis results page. */
export type AnalysisResultPayload = {
  Country: string;
  degree: string;
  yearsOfExp: string;
  /** Readiness score 0–100 for the circular gauge. */
  Performance: number;
  /**
   * Analysis copy: first paragraph is shown as a teaser (with "…") when more paragraphs exist;
   * following paragraphs render below. Same bottom gradient fade as static UI — no CSS blur on text.
   */
  Body: string | string[];
};
