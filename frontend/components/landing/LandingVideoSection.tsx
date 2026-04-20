/**
 * Portrait video section.
 * Video:  public/videos/IMG_3495.MOV
 * Poster: public/videos/IMG_3496.PNG
 */
export function LandingVideoSection() {
  const bullets = [
    "How the questionnaire builds your personalised pathway",
    "Reading and acting on your analysis report",
    "Choosing the right consultation for your stage",
    "Navigating exams, credentials, and state licensing",
  ];

  const stats = [
    { value: "7+", label: "Years of U.S. practice" },
    { value: "3", label: "States licensed" },
    { value: "100%", label: "Profile-based guidance" },
  ];

  return (
    <section
      className="mt-8 w-full scroll-mt-8 border-t border-[#E2E8F0]/80 pt-10 sm:mt-10 sm:pt-12"
      aria-labelledby="landing-video-heading"
    >
      {/* Dark card wraps the whole section */}
      <div className="relative isolate overflow-hidden rounded-3xl bg-[#0c1a3a] px-8 py-10 shadow-[0_32px_80px_-24px_rgba(12,26,58,0.45)] sm:px-10 sm:py-12 lg:px-14 lg:py-14">

        {/* Background glows */}
        <div className="pointer-events-none absolute -left-24 -top-24 h-80 w-80 rounded-full bg-dent-sky/15 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-16 right-0 h-72 w-72 rounded-full bg-[#0ea5e9]/10 blur-3xl" />

        <div className="relative z-1 grid gap-12 lg:grid-cols-[1fr_auto] lg:items-center lg:gap-14">

          {/* ── Left: text ─────────────────────────────────────────── */}
          <div className="min-w-0">
            <p className="text-xs font-bold uppercase tracking-[0.22em] text-dent-sky">
              Product walkthrough
            </p>
            <h2
              id="landing-video-heading"
              className="mt-3 font-display text-2xl font-bold tracking-tight text-white sm:text-3xl lg:text-[2rem]"
            >
              See how DentNav fits your journey
            </h2>
            <p className="mt-4 max-w-xl text-[15px] leading-relaxed text-sky-100/75 sm:text-base">
              A short walkthrough showing how your profile, program type (DDS/Specialty), and different state rules on licensure come
              together into one clear, personalised roadmap — built around your profile.
            </p>

            <ul className="mt-7 space-y-3" aria-label="What you will see">
              {bullets.map((item) => (
                <li key={item} className="flex items-start gap-3 text-sm leading-relaxed text-sky-100/80">
                  <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-dent-sky/20 ring-1 ring-dent-sky/40">
                    <svg viewBox="0 0 10 10" fill="none" className="h-2.5 w-2.5" aria-hidden>
                      <path d="M2 5l2 2 4-4" stroke="#38bdf8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </span>
                  {item}
                </li>
              ))}
            </ul>

            {/* Stats strip */}
            <div className="mt-10 grid grid-cols-3 gap-4 border-t border-white/10 pt-8">
              {stats.map((s) => (
                <div key={s.label}>
                  <p className="font-display text-2xl font-extrabold text-white sm:text-3xl">{s.value}</p>
                  <p className="mt-1 text-[11px] font-medium leading-snug text-sky-100/60">{s.label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* ── Right: gradient glow card ──────────────────────────── */}
          <div className="mx-auto shrink-0 lg:mx-0">
            <div className="relative w-64 sm:w-72">

              {/* Layered ambient glows */}
              <div className="pointer-events-none absolute -inset-8 rounded-[3rem] bg-dent-sky/25 blur-3xl" />
              <div className="pointer-events-none absolute -inset-4 rounded-[2.5rem] bg-[#6366f1]/15 blur-2xl" />

              {/* Gradient border — bg sets the border colour, inner div clips content */}
              <div className="relative rounded-3xl bg-linear-to-br from-dent-sky via-[#818cf8] to-[#006591] p-0.5 shadow-[0_0_48px_-4px_rgba(14,165,233,0.45),0_32px_64px_-16px_rgba(0,0,0,0.6)]">
                <div className="overflow-hidden rounded-[calc(1.5rem-2px)] bg-[#080f20]">

                  {/* Gradient catch-light at top edge */}
                  <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-linear-to-r from-transparent via-white/50 to-transparent" />

                  <video
                    src="/videos/IMG_3495.MOV"
                    poster="/videos/IMG_3496.PNG"
                    controls
                    playsInline
                    preload="metadata"
                    className="block w-full"
                    aria-label="DentNav product walkthrough"
                  />
                </div>
              </div>

              {/* Floating label below */}
              <div className="mt-4 flex justify-center">
                <span className="inline-flex items-center gap-1.5 rounded-full border border-white/15 bg-white/8 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] text-white/50 backdrop-blur-sm">
                  <span className="h-1.5 w-1.5 rounded-full bg-dent-sky" />
                  Product walkthrough
                </span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
