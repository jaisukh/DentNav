import { type NextRequest, NextResponse } from "next/server";

const COOKIE_MAX_AGE = 60 * 60 * 48; // 48h — matches backend JWT expiry

/**
 * Relay endpoint called by the backend OAuth callback.
 *
 * Problem: the backend lives on a different domain (e.g. api.dentnav.com) and
 * sets `dentnav_user_id` scoped to that domain. The Next.js Edge middleware
 * runs on the frontend domain and cannot read cookies from other domains, so
 * it incorrectly sends the user back to /auth/login after sign-in.
 *
 * Solution: the backend redirects here (same frontend domain) and passes the
 * JWT as a query param. This handler re-sets the cookie on the frontend domain
 * so the middleware finds it, then continues to /landing.
 *
 * The backend still sets its own copy of the cookie for API calls that use
 * `credentials: 'include'`. The two cookies are independent (different domains).
 */
export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const token = searchParams.get("token");
  const reclaimedExisting = searchParams.get("reclaimed_existing") === "1";

  const dest = reclaimedExisting ? "/landing?reclaimed_existing=1" : "/landing";
  const response = NextResponse.redirect(new URL(dest, request.url));

  if (token) {
    const isSecure = request.url.startsWith("https://");
    response.cookies.set("dentnav_user_id", token, {
      httpOnly: true,
      sameSite: isSecure ? "none" : "lax",
      secure: isSecure,
      maxAge: COOKIE_MAX_AGE,
      path: "/",
    });
  }

  return response;
}
