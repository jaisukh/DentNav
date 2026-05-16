import { NextResponse } from "next/server";

/** Clears the frontend-domain session cookie on sign-out. */
export async function POST() {
  const response = NextResponse.json({ ok: true });
  response.cookies.delete("dentnav_user_id");
  return response;
}
