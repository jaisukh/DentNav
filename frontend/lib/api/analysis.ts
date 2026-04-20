import type { AnalysisResultPayload } from "@/lib/analysis.types";
import { API_ROUTES } from "./routes";

export type AnalysisRequestBody = {
  answers?: Record<string, unknown>;
};

/** GET — mock analysis payload from Route Handler. */
export async function fetchAnalysis(): Promise<AnalysisResultPayload> {
  const res = await fetch(API_ROUTES.analysis, { cache: "no-store" });
  if (!res.ok) throw new Error(`Analysis request failed: ${res.status}`);
  return res.json() as Promise<AnalysisResultPayload>;
}

/** POST — same mock response; accepts questionnaire answers for future wiring. */
export async function submitAnalysis(body: AnalysisRequestBody): Promise<AnalysisResultPayload> {
  const res = await fetch(API_ROUTES.analysis, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Analysis submit failed: ${res.status}`);
  return res.json() as Promise<AnalysisResultPayload>;
}
