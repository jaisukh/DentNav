import type { QuestionnaireDocument } from "./questionnaire.types";
import questionnaireV1 from "@/data/questionnaire.v1.json";

/**
 * Synchronous fallback (e.g. tests). The app loads the live definition via `fetchQuestionnaire()` → `/api/questionnaire`.
 */
export function getQuestionnaire(): QuestionnaireDocument {
  return questionnaireV1 as QuestionnaireDocument;
}
