import type { AnalysisPreviewPayload } from "@/lib/analysis.types";

const SESSION_KEY = "dentnav:analysis-result";
/** Persists across sessions so the user can return after sign-in/payment. */
const ANALYSIS_ID_LOCAL_KEY = "dentnav:analysis-id";

/** sessionStorage key for one-shot handoff keyed by `?h=` on `/analysis`. */
export const ANALYSIS_HANDOFF_PREFIX = "dentnav:analysis-handoff:";

export function analysisHandoffStorageKey(handoffId: string): string {
  return `${ANALYSIS_HANDOFF_PREFIX}${handoffId}`;
}

/** Persist preview payload after questionnaire submit (until consumed on /analysis). */
export function storeAnalysisResult(payload: AnalysisPreviewPayload): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(payload));
  } catch {
    /* quota / private mode — URL handoff still works */
  }
  try {
    if (payload.analysisId) {
      localStorage.setItem(ANALYSIS_ID_LOCAL_KEY, payload.analysisId);
    }
  } catch {
    /* ignore — analysis page will still render from session */
  }
}

/** Returns the analysisId for the most recent submission, if any. */
export function getStoredAnalysisId(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(ANALYSIS_ID_LOCAL_KEY);
  } catch {
    return null;
  }
}

/** Read handoff payload without removing (safe for React Strict Mode remounts). */
export function peekAnalysisResultFromSession(): AnalysisPreviewPayload | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(SESSION_KEY);
  if (raw === null) return null;
  try {
    return JSON.parse(raw) as AnalysisPreviewPayload;
  } catch {
    return null;
  }
}

export function clearAnalysisResultFromSession(): void {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(SESSION_KEY);
}

export function takeAnalysisResultFromSession(): AnalysisPreviewPayload | null {
  const payload = peekAnalysisResultFromSession();
  if (payload !== null) clearAnalysisResultFromSession();
  return payload;
}
