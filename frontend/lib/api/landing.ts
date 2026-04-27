import {
  getStoredAnalysisId,
  setStoredAnalysisId,
} from "@/lib/analysis-session";
import { API_ROUTES } from "./routes";

export type LandingAccessStatus = {
  signedIn: boolean;
  hasAnsweredQuestionnaire: boolean;
  hasPaid: boolean;
  latestAnalysisId: string | null;
};

/** What :func:`fetchLandingAccessStatus` returns (adds a client-only field from a response header). */
export type LandingAccessResult = LandingAccessStatus & {
  staleQuestionnaireRemoved: boolean;
};

export async function fetchLandingAccessStatus(): Promise<LandingAccessResult> {
  const url = new URL(API_ROUTES.analysisAccessStatus);
  const local = getStoredAnalysisId();
  if (local) {
    url.searchParams.set("local_analysis_id", local);
  }
  const res = await fetch(url.toString(), {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch landing status: ${res.status}`);
  }
  const body = (await res.json()) as LandingAccessStatus;
  return {
    ...body,
    staleQuestionnaireRemoved:
      res.headers.get("X-Removed-Stale-Questionnaire") === "1",
  };
}

/**
 * When the server removed a duplicate unclaimed row, point localStorage at the
 * canonical analysis id the user should keep.
 */
export function applyStaleRemovalSync(result: LandingAccessResult): void {
  if (!result.staleQuestionnaireRemoved) return;
  if (result.signedIn && result.latestAnalysisId) {
    setStoredAnalysisId(result.latestAnalysisId);
  } else {
    setStoredAnalysisId(null);
  }
}

export function toLandingStatus(r: LandingAccessResult): LandingAccessStatus {
  return {
    signedIn: r.signedIn,
    hasAnsweredQuestionnaire: r.hasAnsweredQuestionnaire,
    hasPaid: r.hasPaid,
    latestAnalysisId: r.latestAnalysisId,
  };
}
