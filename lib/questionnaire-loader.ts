import type { QuestionnaireDocument } from "./questionnaire.types";
import questionnaireV1 from "@/data/questionnaire.v1.json";

/**
 * Loads questionnaire definition. Replace with `fetch(url)` when the JSON is hosted on S3.
 */
export function getQuestionnaire(): QuestionnaireDocument {
  return questionnaireV1 as QuestionnaireDocument;
}
