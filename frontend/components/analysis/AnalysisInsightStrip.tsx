import { Fragment } from "react";

const REPORT_CHIPS = [
  { label: "Profile snapshot" },
  { label: "Personalised plan" },
  { label: "Next milestones" },
] as const;

function StepArrow() {
  return (
    <svg
      className="h-3.5 w-3.5 shrink-0 text-sky-400 sm:h-4 sm:w-4"
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden
    >
      <path
        fillRule="evenodd"
        d="M8.22 5.22a.75.75 0 0 1 1.06 0l4.25 4.25a.75.75 0 0 1 0 1.06l-4.25 4.25a.75.75 0 0 1-1.06-1.06L11.94 10 8.22 6.28a.75.75 0 0 1 0-1.06Z"
        clipRule="evenodd"
      />
    </svg>
  );
}

export function AnalysisInsightStrip() {
  return (
    <div className="flex flex-nowrap items-center py-3 gap-2 overflow-x-auto pb-1 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden sm:gap-3">
      <span className="shrink-0 font-display text-[11px] font-semibold uppercase tracking-[0.4px] text-slate-500 sm:text-xs">
        Pathway that fits your profile
      </span>
      <span className="hidden h-4 w-px shrink-0 bg-slate-200 sm:block" aria-hidden />
      {REPORT_CHIPS.map((chip, index) => (
        <Fragment key={chip.label}>
          {index > 0 ? <StepArrow /> : null}
          <span className="shrink-0 rounded-full border border-sky-200/90 bg-white px-2.5 py-1.5 font-display text-[11px] font-bold leading-none text-sky-800 shadow-[0_6px_18px_-10px_rgba(14,165,233,0.55)] transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-[0_10px_24px_-12px_rgba(14,165,233,0.5)] sm:px-3 sm:py-1 sm:text-xs">
            {chip.label}
          </span>
        </Fragment>
      ))}
    </div>
  );
}
