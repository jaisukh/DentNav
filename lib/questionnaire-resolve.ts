import type { AnswerValue, Question, QuestionnaireDocument } from "./questionnaire.types";

/** Resolved option list for a question (static or from degreesByCountry / keys). */
export function resolveQuestionOptions(
  doc: QuestionnaireDocument,
  q: Question,
  answers: Record<string, AnswerValue>,
): string[] {
  if (q.type === "searchableDropdown") {
    if (q.optionsFrom === "keys:degreesByCountry") {
      return Object.keys(doc.degreesByCountry).sort((a, b) => a.localeCompare(b, undefined, { sensitivity: "base" }));
    }
    return [];
  }
  if (q.type === "dropdown") {
    if (q.options?.length) return q.options;
    if (q.dependsOn) {
      const raw = answers[q.dependsOn.questionId];
      const country = typeof raw === "string" ? raw.trim() : "";
      if (!country) return [];
      return doc.degreesByCountry[country] ?? [];
    }
  }
  return [];
}

/** True when the field should be inert until a parent answer exists (e.g. degree after country). */
export function isQuestionDisabled(q: Question, answers: Record<string, AnswerValue>): boolean {
  if (q.type === "dropdown" && q.dependsOn) {
    const raw = answers[q.dependsOn.questionId];
    return typeof raw !== "string" || raw.trim() === "";
  }
  return false;
}
