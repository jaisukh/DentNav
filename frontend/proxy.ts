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
 */
export function proxy(request: NextRequest) {
  const userId = request.cookies.get("dentnav_user_id");

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
