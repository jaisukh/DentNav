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
  /** Preview slice for the signed-in user's latest analysis (no payment required). */
  myAnalysisPreview: `${BACKEND_BASE_URL}/api/v1/analysis/me/preview`,
  /** Raw questionnaire answers for the signed-in user's latest analysis. */
  myAnalysisAnswers: `${BACKEND_BASE_URL}/api/v1/analysis/me/answers`,
  /** Starts Google OAuth on the backend (GET redirects to Google). */
  googleLogin: `${BACKEND_BASE_URL}/api/v1/auth/google/login`,
  /** Clears backend auth cookie for this browser session. */
  googleLogout: `${BACKEND_BASE_URL}/api/v1/auth/google/logout`,
  /** Doctors available for a given service key. */
  serviceDoctors: (serviceKey: string) =>
    `${BACKEND_BASE_URL}/api/v1/services/${encodeURIComponent(serviceKey)}/doctors`,
  /** Availability slots for a doctor-service. */
  doctorAvailability: (doctorServiceId: string) =>
    `${BACKEND_BASE_URL}/api/v1/doctors/${encodeURIComponent(doctorServiceId)}/availability`,
  /** Reserve a slot. */
  reserveSlot: `${BACKEND_BASE_URL}/api/v1/bookings/reserve`,
  /** Release a reservation. */
  releaseSlot: `${BACKEND_BASE_URL}/api/v1/bookings/reserve/release`,
  /** Create a Razorpay order. */
  createOrder: `${BACKEND_BASE_URL}/api/v1/payments/create-order`,
  /** Verify payment after Razorpay modal completes. */
  verifyPayment: `${BACKEND_BASE_URL}/api/v1/payments/verify`,
  /** Cancel a pending_payment booking (user dismissed Razorpay modal). */
  cancelOrder: `${BACKEND_BASE_URL}/api/v1/payments/cancel-order`,
  /** WebSocket for real-time slot updates. */
  slotWs: (doctorServiceId: string) =>
    `${BACKEND_BASE_URL.replace(/^http/, "ws")}/api/v1/doctors/${encodeURIComponent(doctorServiceId)}/availability/ws`,
} as const;
