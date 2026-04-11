"use client";

import type { DropdownQuestion } from "@/lib/questionnaire.types";
import { QuestionBlock } from "../QuestionBlock";
import { SelectChevron } from "../SelectChevron";

type Props = {
  question: DropdownQuestion;
  value: string;
  onChange: (v: string) => void;
  options: string[];
  disabled?: boolean;
};

export function DropdownField({ question, value, onChange, options, disabled }: Props) {
  const ph = question.placeholder ?? "Select an option";
  return (
    <QuestionBlock order={question.order} label={question.label} description={question.description}>
      <div className="relative w-full">
        <select
          id={question.id}
          name={question.id}
          disabled={disabled}
          className="box-border h-9 w-full appearance-none rounded-full border border-slate-300/40 bg-white px-4 pr-10 font-sans text-xs text-[#0C1A3A] focus:border-sky-500 focus:outline-none disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400"
          value={disabled ? "" : value}
          onChange={(e) => onChange(e.target.value)}
        >
          <option value="">{disabled ? "Select a country first" : ph}</option>
          {options.map((opt) => (
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
