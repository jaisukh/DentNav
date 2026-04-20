const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

/** Frontend -> FastAPI backend endpoints. */
export const API_ROUTES = {
  questionnaire: `${BACKEND_BASE_URL}/api/v1/questionnaire`,
  analysis: `${BACKEND_BASE_URL}/api/v1/analysis`,
  googleLogin: `${BACKEND_BASE_URL}/api/v1/auth/google/login`,
} as const;
