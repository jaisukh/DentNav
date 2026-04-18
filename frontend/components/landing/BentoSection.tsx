import type { ReactNode } from "react";

function IconTile({
  children,
  className,
  size = "lg",
}: {
  children: ReactNode;
  className?: string;
  size?: "lg" | "md";
}) {
  const dim =
    size === "lg" ? "h-14 w-14 rounded-2xl" : "h-12 w-12 rounded-xl";
  return (
    <div
      className={`mb-6 flex shrink-0 items-center justify-center ${dim} ${className ?? ""}`}
    >
      {children}
    </div>
  );
}

export function BentoSection() {
  return (
    <section className="bg-dent-surface-bento py-24">
      <div className="page-shell flex flex-col gap-16">
        <div className="flex flex-col gap-4">
          <p className="font-display text-xs font-extrabold uppercase leading-4 tracking-[2.4px] text-dent-sky">
            What we help with
          </p>
          <h2 className="font-display text-balance text-4xl font-extrabold leading-none tracking-[-1.2px] text-dent-ink lg:text-5xl lg:leading-[48px]">
            Everything You Need, In One Place
          </h2>
        </div>

        {/* Figma: 1344px content, 3 equal cols (432px) with 24px gaps, Cell A spans 2 */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Cell A — Application Mastery (spans 2 cols) */}
          <article className="flex min-h-[312px] flex-col justify-between rounded-3xl border border-transparent border-t-4 border-t-dent-sky bg-white p-10 shadow-[0_1px_2px_rgba(0,0,0,0.05)] lg:col-span-2">
            <div>
              <IconTile className="bg-dent-sky/10" size="lg">
                <svg className="h-6 w-6 text-dent-sky" viewBox="0 0 24 24" fill="none" aria-hidden>
                  <rect x="6" y="3" width="12" height="18" rx="1.5" stroke="currentColor" strokeWidth="1.8" />
                  <path d="M9 8h6M9 12h4M9 16h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                  <path d="M14 2l4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                </svg>
              </IconTile>
              <h3 className="text-2xl font-medium leading-8 text-dent-ink">
                Application Mastery
              </h3>
              <p className="mt-2 max-w-[512px] text-base font-normal leading-6 text-[#475569]">
                Strategic guidance for every part of your application to
                ensure you stand out from the competition.
              </p>
            </div>
            <div className="mt-8 flex flex-wrap gap-3">
              {["CAAPID", "SOP", "CV", "INTERVIEW PREP", "ECE", "WES"].map((t) => (
                <span
                  key={t}
                  className="rounded-full bg-dent-badge-bg px-4 py-1.5 text-xs font-bold leading-4 text-dent-deep"
                >
                  {t}
                </span>
              ))}
            </div>
          </article>

          {/* Cell B — We've Been in Your Shoes */}
          <article className="flex min-h-[312px] flex-col rounded-3xl border border-[rgba(14,165,233,0.1)] bg-dent-badge-bg px-8 pb-8 pt-8">
            <IconTile className="bg-white shadow-[0_1px_2px_rgba(0,0,0,0.05)]" size="md">
              <svg className="h-5 w-5 text-dent-deep" viewBox="0 0 24 24" fill="none" aria-hidden>
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                <circle cx="9" cy="7" r="4" stroke="currentColor" strokeWidth="1.8" />
                <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </IconTile>
            <h3 className="text-xl font-medium leading-7 text-dent-ink">
              We&apos;ve Been in Your Shoes
            </h3>
            <p className="mt-3 text-sm leading-relaxed text-[#475569]">
              Like thousands of international dentists, they faced the same overwhelming questions :
            </p>

            {/* Scrolling questions — left to right */}
            <div className="mt-4 overflow-hidden rounded-xl bg-white/60 py-2">
              <div className="animate-marquee-ltr whitespace-nowrap">
                {[
                  "Where do I start?",
                  "Which exams do I take?",
                  "Am I even eligible?",
                  "How do I compete?",
                  "Where do I start?",
                  "Which exams do I take?",
                  "Am I even eligible?",
                  "How do I compete?",
                ].map((q, i) => (
                  <span key={i} className="px-4 text-[11px] font-bold text-dent-deep uppercase tracking-wider">
                    • {q}
                  </span>
                ))}
              </div>
            </div>

            <p className="mt-4 text-xs font-semibold leading-relaxed text-dent-ink/80 italic">
              We've built a step-by-step, hand-holding process to take you from foreign-trained to US-trained Dentist.
            </p>
          </article>

          {/* Cell C — Explore Various Pathways */}
          <article className="flex min-h-[227px] flex-col justify-between rounded-3xl border border-[#F1F5F9] bg-white p-8 shadow-[0_1px_2px_rgba(0,0,0,0.05)] transition-all hover:shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
            <div>
              <IconTile className="bg-dent-badge-bg" size="md">
                <svg className="h-5 w-5 text-dent-deep" viewBox="0 0 24 24" fill="none" aria-hidden>
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.8" />
                  <path d="M16.24 7.76l-2.12 6.36-6.36 2.12 2.12-6.36 6.36-2.12z" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </IconTile>
              <h3 className="text-xl font-medium leading-7 text-dent-ink">
                Explore Various Pathways
              </h3>
              <p className="mt-1 text-sm font-normal leading-5 text-[#64748B]">
                Receive expert guidance for Externships, Observerships, Preceptorship
              </p>
            </div>
            <div className="mt-6 flex flex-wrap gap-2">
              {[
                { label: "DDS/DMD", bg: "bg-blue-50", text: "text-blue-700" },
                { label: "Endo", bg: "bg-purple-50", text: "text-purple-700" },
                { label: "Pros", bg: "bg-emerald-50", text: "text-emerald-700" },
                { label: "Perio", bg: "bg-rose-50", text: "text-rose-700" },
                { label: "Pedo", bg: "bg-amber-50", text: "text-amber-700" },
              ].map((p) => (
                <span
                  key={p.label}
                  className={`rounded-full ${p.bg} px-3 py-1 text-[11px] font-bold uppercase leading-4 tracking-[0.5px] ${p.text}`}
                >
                  {p.label}
                </span>
              ))}
            </div>
          </article>

          {/* Cell D — Visa & Immigration */}
          <article className="flex min-h-[223px] flex-col justify-between rounded-3xl border border-[#F1F5F9] bg-white p-8 shadow-[0_1px_2px_rgba(0,0,0,0.05)] transition-all hover:shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
            <div>
              <IconTile className="bg-dent-badge-bg" size="md">
                <svg className="h-5 w-5 text-dent-deep" viewBox="0 0 24 24" fill="none" aria-hidden>
                  <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
                  <path d="M3 12h18M12 3a14 14 0 0010 9 14 14 0 01-10 9" stroke="currentColor" strokeWidth="1.5" />
                </svg>
              </IconTile>
              <h3 className="text-xl font-medium leading-7 text-dent-ink">
                Visa & Immigration
              </h3>
              <p className="mt-1 text-sm font-normal leading-5 text-[#64748B]">
                Navigate your residency and work authorization with crystal-clear guidance
              </p>
            </div>
            <div className="mt-6 flex flex-wrap gap-2">
              {[
                { label: "O1", bg: "bg-indigo-50", text: "text-indigo-700" },
                { label: "EB1", bg: "bg-violet-50", text: "text-violet-700" },
                { label: "H1", bg: "bg-blue-50", text: "text-blue-700" },
                { label: "F1", bg: "bg-emerald-50", text: "text-emerald-700" },
                { label: "J1", bg: "bg-amber-50", text: "text-amber-700" },
                { label: "B1/B2", bg: "bg-slate-50", text: "text-slate-700" },
              ].map((v) => (
                <span
                  key={v.label}
                  className={`rounded-full ${v.bg} px-3 py-1 text-[11px] font-bold uppercase leading-4 tracking-[0.5px] ${v.text}`}
                >
                  {v.label}
                </span>
              ))}
            </div>
          </article>

          {/* Cell E — Bench Test Training */}
          <article className="relative isolate flex min-h-[270px] flex-col justify-between rounded-3xl bg-gradient-to-br from-dent-ink from-0% to-[#1E293B] to-100% p-8 shadow-[0_20px_25px_-5px_rgba(0,0,0,0.1),0_8px_10px_-6px_rgba(0,0,0,0.1)]">
            <div>
              <IconTile className="bg-white/10 backdrop-blur-md" size="md">
                <svg className="h-[22px] w-[22px] text-white" viewBox="0 0 24 24" fill="none" aria-hidden>
                  <path d="M8 18c2-4 4-6 8-8M12 6l2 4 4 1-3 3 1 4-4-2-4 2 1-4-3-3 4-1 2-4z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
                </svg>
              </IconTile>
              <h3 className="text-xl font-medium leading-7 text-white">
                Bench Test Training
              </h3>
              <p className="mt-2 text-sm font-normal leading-[23px] text-[#94A3B8]">
                Hands-on skill refinement and preparation for the rigorous
                practical assessments.
              </p>
            </div>
            <div className="mt-8">
              <a
                href="#modules"
                className="inline-flex items-center gap-2 text-sm font-bold leading-5 text-dent-sky"
              >
                View Training Modules
                <span aria-hidden>→</span>
              </a>
            </div>
          </article>
        </div>
      </div>
    </section>
  );
}
