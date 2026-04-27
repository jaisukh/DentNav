import type { AnalysisPreviewPayload } from "@/lib/analysis.types";
import type {
  AnswerValue,
  QuestionnaireDocument,
} from "@/lib/questionnaire.types";
import { API_ROUTES } from "./routes";

export type AnalysisRequestBody = {
  answers?: Record<string, unknown>;
};

/**
 * POST the questionnaire answers. The backend persists the full LLM payload
 * server-side and only returns the safe preview slice (readiness score,
 * dimensions, strengths, gaps, profile snapshot, analysisId).
 */
export async function submitAnalysis(
  body: AnalysisRequestBody
): Promise<AnalysisPreviewPayload> {
  const res = await fetch(API_ROUTES.analysis, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    credentials: "include",
  });
  if (!res.ok) throw new Error(`Analysis submit failed: ${res.status}`);
  return res.json() as Promise<AnalysisPreviewPayload>;
}

/** Returns the preview slice for the signed-in user's latest analysis. */
export async function fetchMyAnalysisPreview(): Promise<AnalysisPreviewPayload> {
  const res = await fetch(API_ROUTES.myAnalysisPreview, {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`My analysis preview failed: ${res.status}`);
  return res.json() as Promise<AnalysisPreviewPayload>;
}

export type MyAnswersPayload = {
  questionnaire: QuestionnaireDocument;
  answers: Record<string, AnswerValue>;
};

/** Returns raw answers + questionnaire doc for the signed-in user's latest analysis. */
export async function fetchMyAnalysisAnswers(): Promise<MyAnswersPayload> {
  const res = await fetch(API_ROUTES.myAnalysisAnswers, {
    method: "GET",
    credentials: "include",
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`My answers failed: ${res.status}`);
  return res.json() as Promise<MyAnswersPayload>;
}
