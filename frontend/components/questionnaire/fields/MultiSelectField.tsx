"use client";

import { useMemo } from "react";
import type { MultiSelectQuestion } from "@/lib/questionnaire.types";
import { QuestionBlock } from "../QuestionBlock";
import { SelectChevron } from "../SelectChevron";

type Props = {
  question: MultiSelectQuestion;
  value: string[];
  onChange: (v: string[]) => void;
};

export function MultiSelectField({ question, value, onChange }: Props) {
  const min = question.minSelections ?? 1;
  const max = question.maxSelections;
  const remaining = useMemo(
    () => question.options.filter((o) => !value.includes(o)),
    [question.options, value],
  );
  const atMax = max !== undefined && value.length >= max;

  const add = (opt: string) => {
    if (atMax) return;
    if (!value.includes(opt)) onChange([...value, opt]);
  };

  const remove = (opt: string) => {
    onChange(value.filter((v) => v !== opt));
  };

  return (
    <QuestionBlock order={question.order} label={question.label} description={question.description}>
      <div className="flex w-full flex-wrap gap-2">
        {value.map((tag) => (
          <button
            key={tag}
            type="button"
            className="inline-flex items-center gap-1.5 rounded-full bg-sky-500/20 px-3 py-1.5 text-xs font-bold text-[#003751]"
            onClick={() => remove(tag)}
          >
            {tag}
            <svg width="8" height="8" viewBox="0 0 8 8" fill="none" aria-hidden>
              <path d="M1 1L7 7M1 7L7 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </button>
        ))}
        {remaining.length > 0 && !atMax ? (
          <div className="relative min-w-[140px] flex-1">
            <select
              className="box-border h-9 w-full appearance-none rounded-full border border-slate-300/40 bg-white px-4 pr-10 font-sans text-xs text-[#0C1A3A] focus:border-sky-500 focus:outline-none"
              aria-label={question.placeholder ?? "Add state"}
              value=""
              onChange={(e) => {
                const v = e.target.value;
                if (v) add(v);
              }}
            >
              <option value="">{question.placeholder ?? "Add a state"}</option>
              {remaining.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
            <SelectChevron />
          </div>
        ) : null}
      </div>
      {min > 1 && value.length < min ? (
        <p className="mt-1 text-[11px] font-medium text-sky-500">
          Select at least {min} states ({min - value.length} more needed)
        </p>
      ) : null}
      {max !== undefined && value.length >= max ? (
        <p className="mt-1 text-[11px] font-medium text-slate-500">Maximum {max} states selected.</p>
      ) : null}
    </QuestionBlock>
  );
}
