/**
 * Same-origin Next.js Route Handlers under `app/api/*`.
 * All API logic for this app lives in the frontend repo.
 */
export const API_ROUTES = {
  questionnaire: "/api/questionnaire",
  analysis: "/api/analysis",
  /** Starts Google OAuth (GET redirects to Google). */
  googleLogin: "/api/auth/google/login",
} as const;
