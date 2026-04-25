import Link from "next/link";
import type { ReactNode } from "react";

// ─── Shared micro-icons ───────────────────────────────────────────────────────

function Check({ light = false }: { light?: boolean }) {
  return (
    <svg viewBox="0 0 12 12" fill="none" className="h-2.5 w-2.5" aria-hidden>
      <path
        d="M2.5 6L5 8.5L9.5 3.5"
        stroke={light ? "rgba(255,255,255,0.9)" : "currentColor"}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function Arrow({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg viewBox="0 0 16 16" fill="none" className={className} aria-hidden>
      <path
        d="M3.33 8h9.34M8.67 4l4 4-4 4"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

// ─── Category icons ───────────────────────────────────────────────────────────

function IconClipboard() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" aria-hidden>
      <path
        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M12 12v4M12 8h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function IconGlobe() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" aria-hidden>
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.75" />
      <path
        d="M2 12h20M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
    </svg>
  );
}

function IconMic() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" aria-hidden>
      <rect x="9" y="2" width="6" height="11" rx="3" stroke="currentColor" strokeWidth="1.75" />
      <path
        d="M5 10a7 7 0 0014 0M12 19v3M8 22h8"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconDoc() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" aria-hidden>
      <path
        d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
    </svg>
  );
}

function IconGrad() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" aria-hidden>
      <path
        d="M22 10v6M2 10l10-5 10 5-10 5-10-5z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M6 12v5c0 1.657 2.686 3 6 3s6-1.343 6-3v-5"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconMap() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" aria-hidden>
      <path
        d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0118 0z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="12" cy="10" r="3" stroke="currentColor" strokeWidth="1.75" />
    </svg>
  );
}

function IconAnalysis() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6" aria-hidden>
      <path
        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

// ─── Data ─────────────────────────────────────────────────────────────────────

type ConsultPackage = {
  category: string;
  title: string;
  duration: string;
  sessions: string;
  format: string;
  description: string;
  features: string[];
  outcome: string;
  idealFor: string;
  icon: ReactNode;
  iconClass: string;
  accentBar: string;
  headerGrad: string;
  outcomeGrad: string;
};

const consultPackages: ConsultPackage[] = [
  {
    category: "Foundation",
    title: "Introductory Consultation",
    duration: "45 min",
    sessions: "1 session",
    format: "Live video",
    description:
      "Gain clarity on your current position, discuss your goals and future vision, and walk away with a tailored roadmap — eliminating uncertainty from day one.",
    features: [
      "Clarity assessment of exactly where you stand today",
      "Goal-setting discussion tailored to your background and visa status",
      "Walk away with concrete next steps — not a generic checklist",
      "Reduce trial-and-error with a strategy built for your case",
    ],
    outcome:
      "A clear, personalised strategy that sets the foundation for every step ahead.",
    idealFor: "Anyone beginning their U.S. dentistry journey",
    icon: <IconClipboard />,
    iconClass: "bg-amber-50 text-amber-600 ring-amber-100",
    accentBar: "bg-amber-400",
    headerGrad: "bg-gradient-to-br from-amber-50/70 via-white to-white",
    outcomeGrad: "bg-amber-50/60 ring-1 ring-amber-100",
  },
  {
    category: "Immigration",
    title: "Visa Guidance",
    duration: "60 min",
    sessions: "1 session",
    format: "Live video",
    description:
      "Navigate every U.S. visa pathway with expert guidance rooted in firsthand experience — practical, results-driven advice rather than theoretical information.",
    features: [
      "Student visas (F-1, J-1) and OPT eligibility explained",
      "CAP-GAP, H-1B, and O-1 visa pathways broken down",
      "EB-1 green card and permanent residency strategy",
      "Insider insights from professionals who've navigated these paths themselves",
      "Clear answers to your specific immigration questions",
    ],
    outcome:
      "Informed confidence about which visa pathway fits your situation and exactly what to do next.",
    idealFor: "International dentists managing or planning their U.S. immigration status",
    icon: <IconGlobe />,
    iconClass: "bg-sky-50 text-dent-deep ring-sky-100",
    accentBar: "bg-dent-sky",
    headerGrad: "bg-gradient-to-br from-sky-50/70 via-white to-white",
    outcomeGrad: "bg-sky-50/60 ring-1 ring-sky-100",
  },
  {
    category: "Career",
    title: "Interview Preparation",
    duration: "60 min",
    sessions: "1 session",
    format: "Live mock interviews",
    description:
      "Build the skills, confidence, and clarity to make a lasting impression in any dental residency, AEGD, or clinical interview.",
    features: [
      "Personalised mock interview session",
      "Aligned with your specific career goals and target programmes",
      "In-depth feedback on strengths and areas to improve",
      "Practical, actionable strategies to help you stand out",
      "Techniques to handle unexpected or challenging questions",
    ],
    outcome:
      "Walk into your next interview with confidence, a clear strategy, and the skills to impress.",
    idealFor: "Dentists applying to residencies, AEGD programmes, or clinical roles",
    icon: <IconMic />,
    iconClass: "bg-violet-50 text-violet-600 ring-violet-100",
    accentBar: "bg-violet-400",
    headerGrad: "bg-gradient-to-br from-violet-50/70 via-white to-white",
    outcomeGrad: "bg-violet-50/60 ring-1 ring-violet-100",
  },
  {
    category: "Application",
    title: "CV & SoP Preparation",
    duration: "60 min",
    sessions: "1 session",
    format: "Video session. Documents",
    description:
      "Transform your credentials into a compelling narrative that stands out to admissions committees and employers — with expert support at every step.",
    features: [
      "One-on-one session to deeply understand your journey and goals",
      "Professionally structured CV that highlights your achievements",
      "Statement of Purpose that reflects your story and strengths",
      "First draft delivered within 48 hours of your session",
      "Up to three complimentary revision rounds included",
    ],
    outcome:
      "Polished, compelling application materials tailored to your background and target programme.",
    idealFor: "Dentists applying to U.S. dental programmes or clinical positions",
    icon: <IconDoc />,
    iconClass: "bg-emerald-50 text-emerald-600 ring-emerald-100",
    accentBar: "bg-emerald-400",
    headerGrad: "bg-gradient-to-br from-emerald-50/70 via-white to-white",
    outcomeGrad: "bg-emerald-50/60 ring-1 ring-emerald-100",
  },
  {
    category: "Applications",
    title: "ADEA CAAPID & PASS Guidance",
    duration: "60 min",
    sessions: "1 session",
    format: "Live video",
    description:
      "Navigate the most complex dental program applications with a clear, personalised strategy built around your unique profile and goals.",
    features: [
      "Full application roadmap — timelines, requirements, and key milestones",
      "Guidance customised to your strengths, background, and goals",
      "Smart school selection to identify best-fit programmes",
      "Identify programmes with the highest success chances for your profile",
      "Clarity on DENTPIN creation and credential evaluation steps",
    ],
    outcome:
      "A complete application strategy with full confidence in which programmes to target and how.",
    idealFor: "Foreign-trained dentists seeking advanced dental education in the U.S.",
    icon: <IconGrad />,
    iconClass: "bg-rose-50 text-rose-600 ring-rose-100",
    accentBar: "bg-rose-400",
    headerGrad: "bg-gradient-to-br from-rose-50/70 via-white to-white",
    outcomeGrad: "bg-rose-50/60 ring-1 ring-rose-100",
  },
  {
    category: "Licensing",
    title: "State License Guidance",
    duration: "60 min",
    sessions: "1 session",
    format: "Video · state-specific",
    description:
      "Demystify state licensure as a foreign-trained dentist — with experience-driven guidance that goes beyond what you'll find in official documentation.",
    features: [
      "State-by-state licensure requirement breakdown",
      "Pathways specific to foreign-trained and internationally educated dentists",
      "Florida, Washington, and other high-demand states covered in depth",
      "Clarity on DDS/DMD requirements and available alternatives",
      "Board exam pathways and sequencing by target state",
    ],
    outcome:
      "A clear, actionable picture of exactly what's required to practice in your target state.",
    idealFor: "Dentists ready to pursue licensure in a specific U.S. state",
    icon: <IconMap />,
    iconClass: "bg-teal-50 text-teal-600 ring-teal-100",
    accentBar: "bg-teal-400",
    headerGrad: "bg-gradient-to-br from-teal-50/70 via-white to-white",
    outcomeGrad: "bg-teal-50/60 ring-1 ring-teal-100",
  },
];

// ─── Consult card ─────────────────────────────────────────────────────────────

function ConsultCard({
  category,
  title,
  duration,
  sessions,
  format,
  description,
  features,
  outcome,
  idealFor,
  icon,
  iconClass,
  accentBar,
  headerGrad,
  outcomeGrad,
}: ConsultPackage) {
  return (
    <article className="group relative flex overflow-hidden rounded-2xl border border-[#E2E8F0] bg-white shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:shadow-[0_16px_40px_-12px_rgba(13,28,46,0.12)]">

      {/* Vertical left accent bar */}
      <div className={`w-0.75 shrink-0 self-stretch ${accentBar}`} />

      {/* Inner: stacks on mobile, side-by-side on sm+ */}
      <div className="flex min-w-0 flex-1 flex-col sm:flex-row">

        {/* Left panel — identity + description */}
        <div className={`flex flex-col justify-between border-b border-[#F1F5F9] px-5 py-6 sm:w-[42%] sm:shrink-0 sm:border-b-0 sm:border-r sm:px-6 ${headerGrad}`}>
          <div>
            {/* Icon row */}
            <div className="flex items-start justify-between gap-2">
              <span
                className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ring-1 ${iconClass}`}
                aria-hidden
              >
                {icon}
              </span>
              <div className="flex flex-col items-end gap-1">
                <span className="rounded-full border border-[#E2E8F0] bg-white/80 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-[0.12em] text-[#64748B]">
                  {duration}
                </span>
                <span className="text-[10px] text-[#94A3B8]">{format}</span>
              </div>
            </div>

            {/* Title block */}
            <p className="mt-4 text-[10px] font-bold uppercase tracking-[0.16em] text-[#94A3B8]">
              {category}
            </p>
            <h3 className="mt-1 font-display text-base font-bold leading-snug text-dent-ink">
              {title}
            </h3>
            <p className="mt-2.5 text-[13px] leading-relaxed text-[#64748B]">{description}</p>
          </div>

          {/* Session count badge */}
          <p className="mt-5 text-[11px] font-semibold text-[#94A3B8]">{sessions}</p>
        </div>

        {/* Right panel — features + outcome + CTA */}
        <div className="flex flex-1 flex-col px-5 py-6 sm:px-6">
          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#94A3B8]">
            What&apos;s included
          </p>
          <ul className="mt-3 flex-1 space-y-2.5">
            {features.map((f) => (
              <li key={f} className="flex gap-2.5 text-[13px] leading-snug text-[#475569]">
                <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-dent-badge-bg text-dent-deep ring-1 ring-dent-sky/15">
                  <Check />
                </span>
                {f}
              </li>
            ))}
          </ul>

          {/* Outcome callout */}
          <div className={`mt-5 rounded-xl px-4 py-3 ${outcomeGrad}`}>
            <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#64748B]">
              You&apos;ll walk away with
            </p>
            <p className="mt-1 text-[13px] leading-snug text-[#3E4850]">{outcome}</p>
          </div>

          {/* CTA */}
          <div className="mt-4 space-y-2 border-t border-[#F8FAFC] pt-4">
            <Link
              href="#"
              className="group/btn flex w-full items-center justify-center gap-2 rounded-xl border border-[#E2E8F0] bg-white py-2.5 text-[13px] font-semibold text-dent-ink transition-all hover:border-dent-sky/35 hover:bg-dent-badge-bg/50"
            >
              Book a session
              <Arrow className="h-3.5 w-3.5 transition-transform group-hover/btn:translate-x-0.5" />
            </Link>
            <p className="text-center text-[11px] text-[#94A3B8]">Ideal for: {idealFor}</p>
          </div>
        </div>

      </div>
    </article>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function LandingPackagesPage() {
  return (
    <div className="w-full max-w-6xl pb-14">

      {/* ── Page header ───────────────────────────────────────────────────── */}
      <header className="mb-12">
        <div className="inline-flex items-center gap-2 rounded-full border border-dent-sky/20 bg-dent-badge-bg px-3.5 py-1.5">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-dent-sky" aria-hidden />
          <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-dent-deep">
            Packages
          </span>
        </div>
        <h1 className="mt-4 font-display text-3xl font-bold tracking-tight text-dent-ink sm:text-4xl">
          Everything you need to move forward
        </h1>
        <p className="mt-3 max-w-2xl text-[15px] leading-relaxed text-[#64748B]">
          Start with your personalised pathway analysis, or book a focused consultation session —
          every package is built around your specific background and goals.
        </p>

        {/* Trust strip */}
        <div className="mt-8 flex flex-wrap items-center gap-x-8 gap-y-3">
          {[
            { label: "Tailored to your credentials" },
            { label: "Expert-led sessions" },
            { label: "U.S. dentistry focused" },
          ].map(({ label }) => (
            <div key={label} className="flex items-center gap-2">
              <span className="flex h-4 w-4 items-center justify-center rounded-full bg-dent-badge-bg text-dent-deep ring-1 ring-dent-sky/15">
                <Check />
              </span>
              <span className="text-sm font-medium text-[#475569]">{label}</span>
            </div>
          ))}
        </div>
      </header>

      {/* ── Featured: Analysis Access ──────────────────────────────────────── */}
      <section aria-label="Pathway Analysis Access">
        <div className="relative overflow-hidden rounded-2xl bg-dent-ink shadow-[0_16px_48px_-16px_rgba(12,26,58,0.4)]">
          {/* Decorative radial glow */}
          <div
            className="pointer-events-none absolute right-0 top-0 h-128 w-lg -translate-y-1/4 translate-x-1/4 rounded-full bg-[radial-gradient(circle,rgba(14,165,233,0.18),transparent_65%)]"
            aria-hidden
          />
          <div
            className="pointer-events-none absolute bottom-0 left-1/4 h-64 w-64 translate-y-1/3 rounded-full bg-[radial-gradient(circle,rgba(0,101,145,0.25),transparent_70%)]"
            aria-hidden
          />

          <div className="relative grid gap-10 px-8 py-10 sm:px-12 sm:py-12 lg:grid-cols-[1fr_minmax(0,20rem)] lg:gap-0">

            {/* Left: content */}
            <div className="flex flex-col justify-between lg:pr-12 lg:border-r lg:border-white/10">
              <div>
                {/* Badge */}
                <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3.5 py-1.5">
                  <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#7DD3FC]">
                    One-time access
                  </span>
                </div>

                <h2 className="mt-5 font-display text-2xl font-bold tracking-tight text-white sm:text-[1.75rem] lg:leading-tight">
                  Unlock your personalised pathway analysis
                </h2>
                <p className="mt-3 max-w-lg text-[15px] leading-relaxed text-white/70">
                  Based entirely on your questionnaire responses, your analysis maps the exact exams,
                  documents, and milestones for your case — not a generic checklist.
                </p>
              </div>

              {/* Feature list */}
              <ul className="mt-8 grid gap-3 sm:grid-cols-2">
                {[
                  "Pathway tailored to your credentials and target states",
                  "Exam sequencing with recommended order and timing",
                  "Credential evaluation requirements for your background",
                  "Notes on common bottlenecks and how to navigate them",
                  "Export-friendly structure to share with mentors",
                  "Revisit anytime as your situation evolves",
                ].map((f) => (
                  <li key={f} className="flex gap-2.5 text-sm text-white/80">
                    <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-white/10 ring-1 ring-white/20">
                      <Check light />
                    </span>
                    {f}
                  </li>
                ))}
              </ul>
            </div>

            {/* Right: CTA panel */}
            <div className="flex flex-col items-center justify-center text-center lg:pl-12">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 text-[#7DD3FC] ring-1 ring-white/15">
                <IconAnalysis />
              </div>

              <p className="mt-5 font-display text-lg font-bold text-white">
                Your analysis is ready
              </p>
              <p className="mt-2 text-sm leading-relaxed text-white/60">
                Single purchase — permanent access to your personalised roadmap.
              </p>

              <div className="mt-8 flex w-full flex-col gap-3">
                <Link
                  href="/landing/packages#checkout"
                  className="dentnav-cta-primary group relative flex w-full items-center justify-center gap-2.5 rounded-xl bg-dent-sky py-3.5 text-sm font-bold text-white"
                >
                  <span className="dentnav-cta-primary__halo" aria-hidden />
                  <span className="dentnav-cta-primary__shine" aria-hidden />
                  <span className="relative z-10 flex items-center gap-2.5">
                    Get access
                    <Arrow className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                  </span>
                </Link>
                <Link
                  href="/questionnaire"
                  className="flex w-full items-center justify-center rounded-xl border border-white/15 py-3 text-sm font-semibold text-white/70 transition-colors hover:border-white/30 hover:text-white"
                >
                  Review your questionnaire first
                </Link>
              </div>

              <p className="mt-5 text-[11px] text-white/40">
                Complete the questionnaire to generate your analysis
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Consultation packages ──────────────────────────────────────────── */}
      <section className="mt-20" aria-label="Consultation packages">
        {/* Section heading with ruled lines */}
        <div className="mb-10 flex items-center gap-5">
          <div className="h-px flex-1 bg-[#E2E8F0]" />
          <div className="shrink-0 text-center">
            <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-[#94A3B8]">
              Expert Consultation Sessions
            </p>
            <p className="mt-1 text-sm text-[#64748B]">
              One-on-one guidance for every stage of your journey
            </p>
          </div>
          <div className="h-px flex-1 bg-[#E2E8F0]" />
        </div>

        <div className="grid gap-5 lg:grid-cols-2">
          {consultPackages.map((pkg) => (
            <ConsultCard key={pkg.title} {...pkg} />
          ))}
        </div>

        {/* Bottom note */}
        <div className="mt-10 rounded-2xl border border-[#E2E8F0] bg-white/60 px-6 py-5 text-center backdrop-blur-sm">
          <p className="text-sm text-[#64748B]">
            Not sure which session fits your situation?{" "}
            <Link
              href="#"
              className="font-semibold text-dent-deep underline-offset-2 hover:underline"
            >
              Start with the introductory consultation
            </Link>{" "}
            — it&apos;s the fastest way to map your next steps.
          </p>
        </div>
      </section>
    </div>
  );
}
