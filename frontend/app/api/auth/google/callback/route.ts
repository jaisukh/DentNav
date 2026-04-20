import { NextResponse } from "next/server";

/**
 * OAuth redirect URI handler. Wire token exchange + session when you add persistence.
 * For now: successful return with `code` sends the user to the app shell.
 */
export async function GET(request: Request) {
  const url = new URL(request.url);
  const origin = url.origin;
  const code = url.searchParams.get("code");
  const err = url.searchParams.get("error");

  if (err || !code) {
    return NextResponse.redirect(new URL("/auth/login", origin));
  }

  // TODO: POST to Google token endpoint with GOOGLE_CLIENT_SECRET, set session cookie, etc.
  return NextResponse.redirect(new URL("/landing", origin));
}
