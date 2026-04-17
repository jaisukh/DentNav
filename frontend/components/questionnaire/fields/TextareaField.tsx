"use client";

import type { TextareaQuestion } from "@/lib/questionnaire.types";
import { QuestionBlock } from "../QuestionBlock";

type Props = {
  question: TextareaQuestion;
  value: string;
  onChange: (v: string) => void;
};

export function TextareaField({ question, value, onChange }: Props) {
  return (
    <QuestionBlock order={question.order} label={question.label} description={question.description}>
      <div className="relative w-full">
        <textarea
          id={question.id}
          name={question.id}
          className="box-border w-full min-h-[52px] resize-y rounded-2xl border border-slate-300/60 bg-white px-3.5 py-2.5 font-sans text-xs leading-normal text-[#0C1A3A] placeholder:text-slate-400/70 focus:border-sky-500 focus:outline-none"
          placeholder={question.placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={question.rows ?? 3}
          autoComplete="off"
        />
      </div>
    </QuestionBlock>
  );
}
