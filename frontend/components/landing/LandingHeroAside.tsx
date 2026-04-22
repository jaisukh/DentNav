import { Fragment } from "react";

/** Compact workspace strip — height aligned with hero title + intro (decorative only). */
export function LandingHeroAside() {
  const steps = [
    {
      label: "Responses",
      icon: (
        <svg viewBox="0 0 24 24" fill="none" className="h-3.5 w-3.5" aria-hidden>
          <path
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
          />
        </svg>
      ),
    },
    {
      label: "Package",
      icon: (
        <svg viewBox="0 0 24 24" fill="none" className="h-3.5 w-3.5" aria-hidden>
          <path
            d="M16.5 9.4l-9-5.19M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      ),
    },
    {
      label: "Analysis",
      icon: (
        <svg viewBox="0 0 24 24" fill="none" className="h-3.5 w-3.5" aria-hidden>
          <path
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
          />
        </svg>
      ),
    },
  ];

  return (
    <div
      className="relative isolate mx-auto hidden w-full max-w-[20.5rem] rounded-2xl border border-[#E2E8F0]/90 bg-[#F8FAFC] p-2.5 shadow-[0_16px_40px_-24px_rgba(12,26,58,0.16)] md:block md:shrink-0 lg:mx-0 lg:max-w-[19rem]"
      aria-hidden
    >
      <div className="pointer-events-none absolute inset-0 rounded-2xl bg-[radial-gradient(100%_120%_at_100%_0%,rgba(14,165,233,0.06),transparent_45%)]" />

      <div className="relative z-[1] flex flex-col gap-2">
        <div className="flex items-baseline justify-between gap-2 px-0.5">
          <p className="text-[9px] font-bold uppercase tracking-[0.14em] text-dent-deep">Workspace</p>
          <p className="text-right text-[10px] font-medium leading-snug text-[#64748B]">One flow</p>
        </div>

        <div className="flex items-stretch gap-1">
          {steps.map((step, i) => (
            <Fragment key={step.label}>
              <div className="flex min-w-0 flex-1 flex-col items-center gap-1 rounded-xl border border-[#E2E8F0] bg-white/95 px-1.5 py-2 shadow-sm">
                <span className="text-dent-deep">{step.icon}</span>
                <span className="w-full truncate text-center text-[9px] font-semibold text-dent-ink">{step.label}</span>
              </div>
              {i < steps.length - 1 ? (
                <span className="flex shrink-0 items-center px-0.5 text-[10px] font-bold text-dent-sky/45" aria-hidden>
                  →
                </span>
              ) : null}
            </Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}
