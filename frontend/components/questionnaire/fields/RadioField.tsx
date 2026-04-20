"use client";

import type { RadioQuestion } from "@/lib/questionnaire.types";

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

  const num = String(question.order).padStart(2, "0");

  return (
    <div className="flex w-full flex-col items-start gap-2">
      <div className="flex w-full min-h-6 items-center gap-2">
        <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-sky-100 text-[10px] font-bold text-sky-500">
          {num}
        </div>
        <span className="text-[13px] font-bold leading-snug text-[#0C1A3A]">
          {question.label}
        </span>
      </div>

      {question.description ? (
        <p className="mb-1 w-full text-[11px] font-medium leading-relaxed text-slate-500">
          {question.description}
        </p>
      ) : null}

      {isBinary ? (
        <div className="flex w-full justify-center gap-8">
          {opts.map((opt) => (
            <button
              key={opt}
              type="button"
              onClick={() => onChange(opt)}
              className="flex items-center gap-2.5"
            >
              <span
                className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 transition-all ${
                  value === opt
                    ? "border-sky-500 bg-sky-500"
                    : "border-slate-300 bg-white hover:border-sky-400"
                }`}
              >
                {value === opt && (
                  <span className="h-2 w-2 rounded-full bg-white" />
                )}
              </span>
              <span className={`text-[13px] font-semibold transition-colors ${value === opt ? "text-sky-500" : "text-slate-500"}`}>
                {opt}
              </span>
            </button>
          ))}
        </div>
      ) : (
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
      )}
    </div>
  );
}
