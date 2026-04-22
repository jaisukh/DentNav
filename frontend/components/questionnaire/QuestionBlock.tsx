import type { ReactNode } from "react";

type QuestionBlockProps = {
  order: number;
  label: string;
  description?: string;
  children: ReactNode;
};

export function QuestionBlock({ order, label, description, children }: QuestionBlockProps) {
  const num = String(order).padStart(2, "0");

  return (
    <div className="flex w-full flex-col items-start gap-2">
      <div className="flex w-full min-h-6 items-center gap-2">
        <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-sky-100 text-[10px] font-bold text-sky-500">
          {num}
        </div>
        <span className="text-[13px] font-bold leading-snug text-[#0C1A3A]">{label}</span>
      </div>
      {description ? (
        <p className="mb-1 w-full text-[11px] font-medium leading-relaxed text-slate-500">{description}</p>
      ) : null}
      {children}
    </div>
  );
}
