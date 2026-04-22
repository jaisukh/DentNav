/** Spotlight + stacked frames — decorative video teaser (no fake browser chrome). */
export function LandingVideoAside() {
  return (
    <div
      className="relative isolate mx-auto hidden w-full max-w-[15.5rem] justify-self-center overflow-hidden rounded-2xl border border-[#E2E8F0]/90 bg-gradient-to-br from-[#0c1a3a] via-[#0f2744] to-[#0c4a6e] p-3 shadow-[0_22px_50px_-22px_rgba(12,26,58,0.5)] sm:max-w-[16.5rem] md:flex md:max-w-[17.5rem] md:flex-col md:items-center md:p-4 lg:mx-0"
      aria-hidden
    >
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-[120%] w-[120%] -translate-x-1/2 -translate-y-1/2 bg-[radial-gradient(circle_at_50%_45%,rgba(14,165,233,0.32),transparent_55%)]" />
      <div className="pointer-events-none absolute -bottom-12 right-0 h-36 w-36 rounded-full bg-dent-sky/22 blur-2xl" />

      <div className="relative z-[1] flex w-full flex-col items-center">
        <div className="relative flex h-[7.5rem] w-full items-center justify-center sm:h-[8rem]">
          <span className="absolute h-[5.5rem] w-[5.5rem] rounded-full border border-white/10 sm:h-24 sm:w-24" />
          <span className="absolute h-[4.25rem] w-[4.25rem] rounded-full border border-white/14 sm:h-[4.5rem] sm:w-[4.5rem]" />
          <span className="absolute h-[3.25rem] w-[3.25rem] rounded-full border border-dent-sky/35 sm:h-14 sm:w-14" />

          <div className="relative flex h-12 w-12 items-center justify-center rounded-full bg-white/95 shadow-[0_12px_28px_-10px_rgba(0,0,0,0.35)] ring-2 ring-white/25 sm:h-14 sm:w-14">
            <svg viewBox="0 0 24 24" fill="currentColor" className="ml-0.5 h-6 w-6 text-dent-deep sm:h-7 sm:w-7" aria-hidden>
              <path d="M8 5v14l11-7L8 5z" />
            </svg>
          </div>
        </div>

        <div className="w-full text-center">
          <p className="text-xs font-semibold text-white sm:text-[13px]">Tour recording</p>
          <p className="mt-0.5 text-[10px] leading-snug text-sky-100/90">Full walkthrough lands here</p>
        </div>

        <div className="mt-2.5 flex w-full justify-center gap-1.5">
          <div className="h-9 w-7 rotate-[-6deg] rounded-md border border-white/20 bg-white/10 shadow-md backdrop-blur-sm" />
          <div className="relative z-[1] h-10 w-7 rounded-md border border-white/25 bg-white/15 shadow-lg backdrop-blur-sm" />
          <div className="h-9 w-7 rotate-[6deg] rounded-md border border-white/20 bg-white/10 shadow-md backdrop-blur-sm" />
        </div>
      </div>
    </div>
  );
}
