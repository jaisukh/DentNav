import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json({
    ok: true as const,
    provider: "google",
    message: "Mock sign-in succeeded.",
  });
}
