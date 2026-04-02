"use client";

import type { DropdownQuestion } from "@/lib/questionnaire.types";
import { QuestionBlock } from "../QuestionBlock";
import { SelectChevron } from "../SelectChevron";

type Props = {
  question: DropdownQuestion;
  value: string;
  onChange: (v: string) => void;
};

export function DropdownField({ question, value, onChange }: Props) {
  return (
    <QuestionBlock order={question.order} label={question.label} description={question.description}>
      <div className="relative w-full">
        <select
          id={question.id}
          name={question.id}
          className="box-border h-9 w-full appearance-none rounded-full border border-slate-300/40 bg-white px-4 pr-10 font-sans text-xs text-[#0C1A3A] focus:border-sky-500 focus:outline-none"
          value={value}
          onChange={(e) => onChange(e.target.value)}
        >
          <option value="">{question.placeholder ?? "Select an option"}</option>
          {question.options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
        <SelectChevron />
      </div>
    </QuestionBlock>
  );
}
