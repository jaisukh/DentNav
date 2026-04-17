import type { AnalysisResultPayload } from "@/lib/analysis.types";

const SESSION_KEY = "dentnav:analysis-result";

/** sessionStorage key for one-shot handoff keyed by `?h=` on `/analysis`. */
export const ANALYSIS_HANDOFF_PREFIX = "dentnav:analysis-handoff:";

export function analysisHandoffStorageKey(handoffId: string): string {
  return `${ANALYSIS_HANDOFF_PREFIX}${handoffId}`;
}

/** Persist analysis payload after questionnaire submit (until consumed on /analysis). */
export function storeAnalysisResult(payload: AnalysisResultPayload): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(payload));
  } catch {
    /* quota / private mode — URL handoff still works */
  }
}

/** Read handoff payload without removing (safe for React Strict Mode remounts). */
export function peekAnalysisResultFromSession(): AnalysisResultPayload | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(SESSION_KEY);
  if (raw === null) return null;
  try {
    return JSON.parse(raw) as AnalysisResultPayload;
  } catch {
    return null;
  }
}

export function clearAnalysisResultFromSession(): void {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(SESSION_KEY);
}

/**
 * Read payload placed by the questionnaire flow and remove it (one-shot handoff).
 * Prefer peek + deferred clear on /analysis to avoid losing data under Strict Mode.
 */
export function takeAnalysisResultFromSession(): AnalysisResultPayload | null {
  const payload = peekAnalysisResultFromSession();
  if (payload !== null) clearAnalysisResultFromSession();
  return payload;
}
