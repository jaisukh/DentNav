/**
 * Brochure download card — shown in the hero aside on the landing home page.
 * Wire `href` to the real PDF path once the file is placed in public/.
 */
export function BrochureDownload() {
  return (
    <div
      className="relative isolate hidden w-full rounded-2xl border border-[#E2E8F0]/90 bg-[#F8FAFC] p-4 shadow-[0_16px_40px_-24px_rgba(12,26,58,0.16)] md:flex md:w-56 md:shrink-0 md:flex-col lg:mx-0 lg:w-64"
      aria-label="Download DentNav brochure"
    >
      {/* Subtle radial highlight */}
      <div className="pointer-events-none absolute inset-0 rounded-2xl bg-[radial-gradient(100%_120%_at_100%_0%,rgba(14,165,233,0.06),transparent_50%)]" />

      <div className="relative z-[1] flex flex-1 flex-col gap-3">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-[9px] font-bold uppercase tracking-[0.14em] text-dent-deep">Free download</p>
            <p className="mt-0.5 text-sm font-bold leading-snug text-dent-ink">DentNav Brochure</p>
          </div>
          {/* PDF badge */}
          <span className="shrink-0 rounded-lg border border-rose-100 bg-rose-50 px-2 py-1 text-[10px] font-bold uppercase tracking-wide text-rose-500">
            PDF
          </span>
        </div>

        {/* Document preview */}
        <div className="flex items-center gap-3 rounded-xl border border-[#E2E8F0] bg-white px-3 py-3 shadow-sm">
          {/* Page icon */}
          <div className="flex h-10 w-8 shrink-0 flex-col overflow-hidden rounded-md border border-[#DBEAFE] bg-gradient-to-b from-[#EFF6FF] to-white shadow-sm">
            <div className="h-1.5 w-full bg-dent-deep/80" />
            <div className="flex flex-1 flex-col justify-center gap-0.5 px-1 py-1">
              <div className="h-0.5 w-full rounded-full bg-[#CBD5E1]" />
              <div className="h-0.5 w-4/5 rounded-full bg-[#CBD5E1]" />
              <div className="h-0.5 w-3/5 rounded-full bg-[#CBD5E1]" />
            </div>
          </div>
          <div className="min-w-0">
            <p className="truncate text-[11px] font-semibold text-dent-ink">DentNav_Guide_2026.pdf</p>
            <p className="mt-0.5 text-[10px] text-[#94A3B8]">Complete U.S. dental pathway guide</p>
          </div>
        </div>

        {/* What's inside */}
        <ul className="flex-1 space-y-1.5 px-0.5">
          {[
            "Pathways for foreign-trained dentists",
            "Exam timelines & state licensing",
            "Visa & credential guidance overview",
          ].map((item) => (
            <li key={item} className="flex items-start gap-2 text-[11px] leading-snug text-[#475569]">
              <svg viewBox="0 0 12 12" fill="none" className="mt-px h-3 w-3 shrink-0 text-dent-sky" aria-hidden>
                <path d="M2 6l2.5 2.5L10 3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              {item}
            </li>
          ))}
        </ul>

        {/* Download button */}
        <a
          href="/brochure.pdf"
          download="DentNav_Guide_2026.pdf"
          className="flex items-center justify-center gap-2 rounded-xl bg-dent-deep px-4 py-2.5 text-xs font-bold text-white shadow-[0_6px_18px_-8px_rgba(0,101,145,0.7)] transition-all duration-200 hover:-translate-y-px hover:brightness-110 active:scale-[0.98]"
        >
          <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5" aria-hidden>
            <path d="M8 2v8M4.5 6.5L8 10l3.5-3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M2.5 12.5h11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          Download Free Monograph
        </a>
      </div>
    </div>
  );
}
