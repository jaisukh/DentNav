import type { QuestionnaireDocument } from "@/lib/questionnaire.types";
import { API_ROUTES } from "./routes";

export async function fetchQuestionnaire(): Promise<QuestionnaireDocument> {
  const res = await fetch(API_ROUTES.questionnaire, { cache: "no-store" });
  if (!res.ok) throw new Error(`Questionnaire request failed: ${res.status}`);
  return res.json() as Promise<QuestionnaireDocument>;
}
