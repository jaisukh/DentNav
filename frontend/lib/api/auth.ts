import { getStoredAnalysisId } from "@/lib/analysis-session";
import { API_ROUTES } from "./routes";

/**
 * Sign-in entry. Sends the user to the backend OAuth start endpoint, which
 * then redirects to Google's consent screen.
 *
 * If the user already submitted the questionnaire anonymously, we forward
 * that `analysisId` so the backend can link the stored row to their account
 * (OAuth `state` round-trips it through Google back to `/callback`).
 */
export function getGoogleSignInUrl(): string {
  const base = API_ROUTES.googleLogin;
  const analysisId = getStoredAnalysisId();
  if (!analysisId) return base;
  const separator = base.includes("?") ? "&" : "?";
  return `${base}${separator}analysis_id=${encodeURIComponent(analysisId)}`;
}

export async function signOut(): Promise<void> {
  try {
    await fetch(API_ROUTES.googleLogout, {
      method: "POST",
      credentials: "include",
    });
  } catch {
    // Ignore network errors here; caller still redirects user to public page.
  }
}
