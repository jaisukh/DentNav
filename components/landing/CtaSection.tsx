import Link from "next/link";

export function CtaSection() {
  return (
    <section className="relative isolate overflow-hidden bg-white py-24">
      <div
        className="pointer-events-none absolute left-1/2 top-1/2 z-0 flex -translate-x-1/2 -translate-y-1/2 items-center justify-center"
        aria-hidden
      >
        <div className="relative flex h-[400px] w-[400px] items-center justify-center rounded-full border border-[rgba(14,165,233,0.1)]">
          <div className="absolute left-1/2 top-1/2 h-[649px] w-[649px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[rgba(14,165,233,0.1)]" />
          <div className="absolute left-1/2 top-1/2 h-[842px] w-[842px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-[rgba(14,165,233,0.1)]" />
        </div>
      </div>

      {/* Figma: padding 96px 192px, container max-w 896px centered */}
      <div className="page-shell relative z-[1]">
        <div className="mx-auto flex w-full max-w-[1058px] flex-col items-center gap-10 text-center">
          <h2 className="max-w-[691px] font-display text-balance text-4xl font-extrabold leading-none tracking-[-1.2px] text-dent-ink lg:text-5xl lg:leading-[48px]">
            Ready to Start Your U.S. Dental Journey?
          </h2>
          <p className="max-w-[814px] text-lg font-medium leading-7 text-[#475569]">
            Explore all pathways built by U.S. licensed dentists. Step-by-step guidance to the very end.
          </p>
          <div className="flex w-full flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/questionnaire"
              className="relative isolate inline-flex items-center justify-center rounded-full bg-[linear-gradient(99.11deg,#006591_0%,#0EA5E9_100%)] px-10 py-5 text-base font-bold leading-6 text-white shadow-[0_20px_25px_-5px_rgba(0,101,145,0.25),0_8px_10px_-6px_rgba(0,101,145,0.2)] transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_25px_30px_-5px_rgba(0,101,145,0.25)] active:scale-[0.98]"
            >
              Unlock Your Custom Plan
            </Link>
            <a
              href="#expert"
              className="inline-flex items-center justify-center rounded-full border-2 border-[rgba(14,165,233,0.3)] bg-white px-10 py-5 text-base font-bold leading-6 text-dent-deep transition-all duration-300 hover:-translate-y-1 hover:bg-slate-50 hover:border-[rgba(14,165,233,0.5)] active:scale-[0.98]"
            >
              Talk to an Expert
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
