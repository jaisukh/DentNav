/**
 * Backend (FastAPI) endpoints. URL is baked at build time via NEXT_PUBLIC_BACKEND_URL.
 * For local dev set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000 in `.env.local`.
 */
const BACKEND_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export const API_ROUTES = {
  questionnaire: `${BACKEND_BASE_URL}/api/v1/questionnaire`,
  analysis: `${BACKEND_BASE_URL}/api/v1/analysis`,
  analysisAccessStatus: `${BACKEND_BASE_URL}/api/v1/analysis/access-status`,
  /** Starts Google OAuth on the backend (GET redirects to Google). */
  googleLogin: `${BACKEND_BASE_URL}/api/v1/auth/google/login`,
  /** Clears backend auth cookie for this browser session. */
  googleLogout: `${BACKEND_BASE_URL}/api/v1/auth/google/logout`,
} as const;
