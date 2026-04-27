import { type NextRequest, NextResponse } from "next/server";

/**
 * Route guard for the authenticated landing shell (/landing/**).
 *
 * Runs on the Edge before the page renders. Checks for the
 * `dentnav_user_id` httpOnly cookie that the FastAPI backend sets after a
 * successful Google OAuth callback.
 *
 * If the cookie is absent the user is redirected to the sign-in page
 * immediately — no flash of the protected layout.
 *
 * If the cookie is present the request is forwarded. The AuthGuard client
 * component inside the landing layout then calls /api/v1/analysis/access-status
 * to confirm the session is still valid with the backend, and handles the
 * case where the cookie exists but the session has expired.
 *
 * NOTE: Next.js requires this file to be named `middleware.ts` (or .js) and
 * exports a function named `middleware` — both are required for the runtime
 * to register it. Renaming either will silently disable the guard.
 */
export function middleware(request: NextRequest) {
  const userId = request.cookies.get("dentnav_user_id");
  // Presence only: Edge cannot verify JWT signature or expiry. Malformed,
  // expired, or tampered values still have a value here — `AuthGuard` +
  // `/access-status` validate with the backend; users with a bad cookie may
  // see a brief flash of the protected shell before redirect.

  if (!userId?.value) {
    const loginUrl = new URL("/auth/login", request.url);
    // Preserve the intended destination so it can be used after sign-in
    // once the backend OAuth callback supports dynamic redirect URLs.
    loginUrl.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/landing/:path*"],
};
