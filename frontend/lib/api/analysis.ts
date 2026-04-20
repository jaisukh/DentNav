import type { AnalysisPreviewPayload } from "@/lib/analysis.types";
import { API_ROUTES } from "./routes";

export type AnalysisRequestBody = {
  answers?: Record<string, unknown>;
};

/**
 * POST the questionnaire answers. The backend persists the full LLM payload
 * server-side and only returns the safe preview slice (readiness score,
 * dimensions, strengths, gaps, profile snapshot, analysisId).
 */
export async function submitAnalysis(
  body: AnalysisRequestBody
): Promise<AnalysisPreviewPayload> {
  const res = await fetch(API_ROUTES.analysis, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    credentials: "include",
  });
  if (!res.ok) throw new Error(`Analysis submit failed: ${res.status}`);
  return res.json() as Promise<AnalysisPreviewPayload>;
}
