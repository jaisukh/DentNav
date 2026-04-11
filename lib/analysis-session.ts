import type { AnalysisResultPayload } from "@/lib/analysis.types";

const SESSION_KEY = "dentnav:analysis-result";

/** Persist analysis payload after questionnaire submit (until consumed on /analysis). */
export function storeAnalysisResult(payload: AnalysisResultPayload): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(payload));
}

/**
 * Read payload placed by the questionnaire flow and remove it (one-shot handoff).
 * Returns null if missing or invalid — caller should fall back to fetching.
 */
export function takeAnalysisResultFromSession(): AnalysisResultPayload | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(SESSION_KEY);
  if (raw === null) return null;
  sessionStorage.removeItem(SESSION_KEY);
  try {
    return JSON.parse(raw) as AnalysisResultPayload;
  } catch {
    return null;
  }
}
