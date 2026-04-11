import { NextResponse } from "next/server";
import analysisMock from "@/data/analysis-mock.json";
import type { AnalysisResultPayload } from "@/lib/analysis.types";

export function GET() {
  return NextResponse.json(analysisMock as AnalysisResultPayload);
}

export async function POST(request: Request) {
  try {
    await request.json().catch(() => ({}));
  } catch {
    /* optional body */
  }
  return NextResponse.json(analysisMock as AnalysisResultPayload);
}
