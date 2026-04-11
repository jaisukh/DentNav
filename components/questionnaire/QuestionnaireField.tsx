"use client";

import type { Question, QuestionnaireDocument } from "@/lib/questionnaire.types";
import type { AnswerValue } from "@/lib/questionnaire.types";
import { isQuestionDisabled, resolveQuestionOptions } from "@/lib/questionnaire-resolve";
import { TextareaField } from "./fields/TextareaField";
import { DropdownField } from "./fields/DropdownField";
import { RadioField } from "./fields/RadioField";
import { MultiSelectField } from "./fields/MultiSelectField";
import { SearchableDropdownField } from "./fields/SearchableDropdownField";

type Props = {
  doc: QuestionnaireDocument;
  question: Question;
  value: AnswerValue | undefined;
  answers: Record<string, AnswerValue>;
  onChange: (id: string, v: AnswerValue) => void;
};

export function QuestionnaireField({ doc, question, value, answers, onChange }: Props) {
  switch (question.type) {
    case "textarea":
      return (
        <TextareaField
          question={question}
          value={typeof value === "string" ? value : ""}
          onChange={(v) => onChange(question.id, v)}
        />
      );
    case "searchableDropdown":
      return (
        <SearchableDropdownField
          question={question}
          value={typeof value === "string" ? value : ""}
          onChange={(v) => onChange(question.id, v)}
          options={resolveQuestionOptions(doc, question, answers)}
        />
      );
    case "dropdown": {
      const disabled = isQuestionDisabled(question, answers);
      return (
        <DropdownField
          question={question}
          value={typeof value === "string" ? value : ""}
          onChange={(v) => onChange(question.id, v)}
          options={resolveQuestionOptions(doc, question, answers)}
          disabled={disabled}
        />
      );
    }
    case "radio":
      return (
        <RadioField
          question={question}
          value={typeof value === "string" ? value : ""}
          onChange={(v) => onChange(question.id, v)}
        />
      );
    case "multiSelect":
      return (
        <MultiSelectField
          question={question}
          value={Array.isArray(value) ? value : []}
          onChange={(v) => onChange(question.id, v)}
        />
      );
    default:
      return null;
  }
}
