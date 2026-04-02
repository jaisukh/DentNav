"use client";

import type { Question } from "@/lib/questionnaire.types";
import type { AnswerValue } from "@/lib/questionnaire.types";
import { TextareaField } from "./fields/TextareaField";
import { DropdownField } from "./fields/DropdownField";
import { RadioField } from "./fields/RadioField";
import { MultiSelectField } from "./fields/MultiSelectField";

type Props = {
  question: Question;
  value: AnswerValue | undefined;
  onChange: (id: string, v: AnswerValue) => void;
};

export function QuestionnaireField({ question, value, onChange }: Props) {
  switch (question.type) {
    case "textarea":
      return (
        <TextareaField
          question={question}
          value={typeof value === "string" ? value : ""}
          onChange={(v) => onChange(question.id, v)}
        />
      );
    case "dropdown":
      return (
        <DropdownField
          question={question}
          value={typeof value === "string" ? value : ""}
          onChange={(v) => onChange(question.id, v)}
        />
      );
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
