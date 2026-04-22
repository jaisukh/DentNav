import { API_ROUTES } from "./routes";

export type LandingAccessStatus = {
  signedIn: boolean;
  hasAnsweredQuestionnaire: boolean;
  hasPaid: boolean;
  latestAnalysisId: string | null;
};

export async function fetchLandingAccessStatus(): Promise<LandingAccessStatus> {
  const res = await fetch(API_ROUTES.analysisAccessStatus, {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch landing status: ${res.status}`);
  }
  return res.json() as Promise<LandingAccessStatus>;
}
