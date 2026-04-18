"use client";

import type { RadioQuestion } from "@/lib/questionnaire.types";
import { QuestionBlock } from "../QuestionBlock";

type Props = {
  question: RadioQuestion;
  value: string;
  onChange: (v: string) => void;
};

const pillBase =
  "box-border flex h-9 cursor-pointer items-center justify-center rounded-full border border-slate-300/50 bg-white px-4 text-xs font-medium text-[#0C1A3A] transition-all";
const pillActive = "border-sky-500 bg-sky-500/5 font-semibold text-sky-500";

export function RadioField({ question, value, onChange }: Props) {
  const opts = question.options;
  const isBinary =
    opts.length === 2 &&
    opts.some((o) => o.toLowerCase() === "yes") &&
    opts.some((o) => o.toLowerCase() === "no");

  if (isBinary) {
    const num = String(question.order).padStart(2, "0");

    return (
      <div className="box-border flex w-full flex-col gap-3 rounded-[36px] border border-sky-500/10 bg-sky-50/40 p-3">
        <div className="flex w-full flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex min-w-0 flex-1 items-start gap-2">
            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-sky-100 text-[10px] font-bold text-sky-500">
              {num}
            </div>
            <span className="min-w-0 flex-1 text-left text-[13px] font-bold leading-snug text-[#0C1A3A]">
              {question.label}
            </span>
          </div>
          <div className="box-border flex h-[38px] w-[140px] shrink-0 self-end rounded-full border border-slate-200/80 bg-white p-1 sm:self-center">
            {opts.map((opt) => (
              <button
                key={opt}
                type="button"
                className={`flex flex-1 items-center justify-center rounded-full border-0 text-[11px] font-medium transition-colors ${
                  value === opt
                    ? "bg-sky-500 font-bold text-white"
                    : "bg-transparent text-slate-400 hover:text-slate-600"
                }`}
                onClick={() => onChange(opt)}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>
        {question.description ? (
          <p className="text-[11px] font-medium leading-relaxed text-slate-500">{question.description}</p>
        ) : null}
      </div>
    );
  }

  return (
    <QuestionBlock order={question.order} label={question.label} description={question.description}>
      <div className="flex w-full flex-wrap gap-2">
        {opts.map((opt) => (
          <button
            key={opt}
            type="button"
            className={`${pillBase} ${value === opt ? pillActive : ""}`}
            onClick={() => onChange(opt)}
          >
            {opt}
          </button>
        ))}
      </div>
    </QuestionBlock>
  );
}
