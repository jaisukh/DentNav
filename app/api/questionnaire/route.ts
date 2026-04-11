import { NextResponse } from "next/server";
import questionnaireV1 from "@/data/questionnaire.v1.json";
import type { QuestionnaireDocument } from "@/lib/questionnaire.types";

export function GET() {
  return NextResponse.json(questionnaireV1 as QuestionnaireDocument);
}
