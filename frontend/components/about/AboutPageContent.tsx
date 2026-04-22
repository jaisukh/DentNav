import Image from "next/image";
import Link from "next/link";

// ─── Types & data ─────────────────────────────────────────────────────────────

type Founder = {
  name: string;
  role: string;
  profile: string;
  photoSrc: string;
  photoAlt: string;
  intro: string;
  story: string[];

  outcomes: string[];
  focus: string[];
  quote: string;
  instagram?: string;
};

const founders: Founder[] = [
  {
    name: "Dr. Venkata Ratna Kumar Rudravaram",
    role: "Co-Founder, DentNav",
    profile: "Licensed Dentist (CA, VA, WA)",
    photoSrc: "/images/founders/rudravaram.png",
    photoAlt:
      "Dr. Venkata Ratna Kumar Rudravaram, professional headshot in a navy suit and tie",
    intro:
      "Dr. Rudravaram's journey is a blueprint for possibility for foreign-trained dentists.",
    story: [
      "Raised in a small town in Andhra Pradesh, India, he studied in Telugu-medium schools where English was a challenge, then pursued dentistry in a government college with limited clinical exposure and infrastructure.",
      "When he moved toward a U.S. pathway, he faced uncertainty around visas, pathways, eligibility, and finances, alongside academic setbacks including failure during BDS.",
      "Through persistence, self-learning, and strategic decisions, he built a successful U.S. path pursuing AEGD program.",
    ],
    outcomes: [
      "Graduated from world's first dental school",
      "Obtained dental licenses in California, Virginia, and Washington",
      "Practiced successfully as a general dentist in the U.S. for 7+ years",
    ],
    focus: [
      "Clear understanding of U.S. dental pathways",
      "Right strategy based on profile and goals",
      "Avoiding costly mistakes and misinformation",
      "Building realistic, confident plans at any life stage",
    ],
    quote:
      "Whether you are in your 20s, 30s, 40s, or even 50s, it is not too late. The only mistake is not starting with the right guidance.",
    instagram: "https://www.instagram.com/dr.rudravaram/",
  },
  {
    name: "Dr. Anuja Singaraju",
    role: "Co-Founder, DentNav",
    profile:
      "Pediatric Dentist | Resident, Loma Linda University School of Dentistry",
    photoSrc: "/images/founders/singaraju.png",
    photoAlt:
      "Dr. Anuja Singaraju, professional headshot in a black blazer and white blouse",
    intro:
      "Dr. Anuja's journey reflects clarity, preparation, and focused execution.",
    story: [
      "As a trained pediatric dentist (MDS) from India, she had strong academics and clinical depth, but recognized early that succeeding in the U.S. system needs a different strategy.",
      "She aligned her pathway to her strengths, prepared intentionally for exams, applications, and interviews, and avoided applying without direction.",
      "That focused preparation helped her secure a postdoctoral pediatric dentistry program admission at Loma Linda University School of Dentistry on her first attempt.",
    ],
    outcomes: [
      "Cleared required exams",
      "Navigated applications efficiently",
      "Secured postdoctoral pediatric dentistry admission on first attempt",
    ],
    focus: [
      "Specialty pathway planning",
      "Application and interview strategy",
      "Academic positioning that programs value",
      "Choosing DDS vs residency based on personal goals",
    ],
    quote:
      "It is not about choosing the most popular path. It is about choosing the right path for you.",
    instagram: "https://www.instagram.com/dr.anuja.singaraju/",
  },
];

const philosophy = [
  "There is no single pathway to becoming a dentist in the U.S.",
  "Your journey depends on profile, strategy, and guidance, not myths.",
  "You can start in your 20s, 30s, 40s, or beyond.",
  "The right mentor can save years of confusion and thousands of dollars.",
];

// ─── Shared CTA props ─────────────────────────────────────────────────────────

type AboutPageContentProps = {
  /** CTA shown alongside "Start Your Guidance Plan". Defaults to the sign-in link. */
  secondaryCta?: React.ReactNode;
};

// ─── Component ────────────────────────────────────────────────────────────────

export function AboutPageContent({ secondaryCta }: AboutPageContentProps) {
  return (
    <>
      {/* Hero */}
      <section className="relative border-b bg-gradient-to-b from-white via-sky-50 to-white border-sky-100/10">
        <div className="page-shell py-20 sm:py-24">
          <div className="mx-auto flex max-w-[980px] flex-col gap-6 text-center">
            <span className="mx-auto inline-flex rounded-full border border-[#BAE6FD] bg-[#F0F9FF] px-4 py-1.5 text-xs font-bold uppercase tracking-[1.2px] text-[#0369A1]">
              About DentNav
            </span>
            <h1 className="font-display text-4xl font-extrabold leading-tight tracking-[-1px] text-[#0C1A3A] sm:text-5xl">
              Because We Know the Struggle
            </h1>
            <p className="mx-auto max-w-[860px] text-balance text-lg font-medium italic leading-8 text-[#334155]">
              &ldquo;We have been in your shoes. We know the confusion, the fear,
              and the misinformation. DentNav was built to answer one question
              with clarity: yes, your U.S. dental dream is possible.&rdquo;
            </p>
            <div className="mx-auto mt-2 max-w-[880px] rounded-3xl border border-[#DCEBFF] bg-white/85 px-6 py-6 shadow-[0_18px_40px_-26px_rgba(2,132,199,0.28)] transition-all duration-300 hover:-translate-y-0.5 hover:shadow-[0_24px_56px_-26px_rgba(2,132,199,0.34)] sm:px-8 sm:py-7">
              <p className="text-balance text-base font-medium leading-7 text-[#334155] sm:text-lg sm:leading-8">
                &quot;There is no single path to becoming a dentist in the United
                States. There are multiple pathways, DDS/DMD, residencies,
                limited licenses, and academic roles. The right path depends on
                your background, goals, and strategy. The difference between
                struggle and success is not talent, it is guidance. That is
                where we come in.&quot;
              </p>
            </div>
            <div className="mt-2 grid gap-3 sm:grid-cols-3">
              {[
                { label: "Licensed U.S. Experience", value: "7+ Years" },
                { label: "States Licensed", value: "CA • VA • WA" },
                { label: "Mentorship Focus", value: "Profile-Based Paths" },
              ].map((stat) => (
                <div
                  key={stat.label}
                  className="rounded-2xl border border-[#DBEAFE] bg-white/80 px-4 py-3 text-left shadow-[0_8px_20px_-18px_rgba(15,23,42,0.5)] transition-all duration-300 hover:-translate-y-0.5 hover:border-[#93C5FD] hover:bg-white hover:shadow-[0_16px_30px_-20px_rgba(14,116,144,0.45)]"
                >
                  <p className="text-xs font-semibold uppercase tracking-[0.9px] text-[#0369A1]">
                    {stat.label}
                  </p>
                  <p className="mt-1 text-sm font-bold text-[#0F172A]">
                    {stat.value}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="page-shell py-16 sm:py-20">
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="group rounded-3xl border border-[#E2E8F0] bg-white p-7 shadow-[0_18px_40px_-28px_rgba(15,23,42,0.25)] transition-all duration-300 hover:-translate-y-1 hover:border-[#BFDBFE] hover:shadow-[0_24px_50px_-26px_rgba(14,116,144,0.3)] sm:p-8">
            <h2 className="font-display text-2xl font-bold tracking-[-0.6px] text-[#0C1A3A] sm:text-[30px]">
              Mission
            </h2>
            <p className="mt-4 text-base font-medium leading-7 text-[#475569]">
              To guide every international dentist, starting from their home
              country, toward practicing or specializing in the United States
              without losing years in confusion and trial-and-error.
            </p>
          </div>
          <div className="group rounded-3xl border border-[#E2E8F0] bg-white p-7 shadow-[0_18px_40px_-28px_rgba(15,23,42,0.25)] transition-all duration-300 hover:-translate-y-1 hover:border-[#BFDBFE] hover:shadow-[0_24px_50px_-26px_rgba(14,116,144,0.3)] sm:p-8">
            <h2 className="font-display text-2xl font-bold tracking-[-0.6px] text-[#0C1A3A] sm:text-[30px]">
              Vision
            </h2>
            <p className="mt-4 text-base font-medium leading-7 text-[#475569]">
              No dentist should abandon their dream of studying or working in
              the USA because the process feels too complicated.
            </p>
          </div>
        </div>
      </section>

      {/* Founders */}
      <section className="page-shell pb-16 sm:pb-20">
        <div className="mb-10 text-center sm:mb-12">
          <h2 className="font-display text-3xl font-extrabold tracking-[-0.8px] text-[#0C1A3A] sm:text-4xl">
            Meet the Founders
          </h2>
          <p className="mx-auto mt-3 max-w-[760px] text-base font-medium leading-7 text-[#64748B] sm:text-lg">
            Real journeys. Real decisions. Real strategies that work.
          </p>
        </div>

        <div className="space-y-8">
          {founders.map((founder) => (
            <article
              key={founder.name}
              className="group relative overflow-hidden rounded-[28px] border border-[#E2E8F0] bg-white p-6 shadow-[0_24px_64px_-34px_rgba(15,23,42,0.28)] transition-all duration-300 hover:-translate-y-0.5 hover:border-[#BFDBFE] hover:shadow-[0_28px_72px_-30px_rgba(14,116,144,0.3)] sm:p-8"
            >
              <div
                className="pointer-events-none absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-[#7DD3FC] via-[#38BDF8] to-[#0EA5E9] opacity-0 transition-opacity duration-300 group-hover:opacity-100"
                aria-hidden
              />
              <div className="grid gap-7 lg:grid-cols-[320px_1fr] lg:gap-10">
                <div className="space-y-4">
                  <div className="group/photo relative aspect-[4/5] w-full overflow-hidden rounded-2xl border-2 border-[#BFDBFE] bg-[#F0F9FF] shadow-[0_12px_32px_-20px_rgba(14,116,144,0.35)] transition-all duration-300 hover:border-[#7DD3FC] hover:shadow-[0_16px_40px_-18px_rgba(14,116,144,0.4)]">
                    <Image
                      src={founder.photoSrc}
                      alt={founder.photoAlt}
                      fill
                      className="object-cover object-top transition-transform duration-300 group-hover/photo:scale-[1.02]"
                      sizes="(max-width: 1024px) 100vw, 320px"
                      priority={founder.name.includes("Rudravaram")}
                    />
                  </div>
                  <div className="rounded-2xl border border-[#DBEAFE] bg-[#F8FBFF] p-4">
                    <h3 className="font-display text-xl font-bold tracking-[-0.4px] text-[#0C1A3A]">
                      {founder.name}
                    </h3>
                    <p className="mt-1 text-sm font-semibold uppercase tracking-[0.8px] text-[#0369A1]">
                      {founder.role}
                    </p>
                    <p className="mt-1 text-sm font-medium text-[#64748B]">
                      {founder.profile}
                    </p>
                    {founder.instagram && (
                      <a
                        href={founder.instagram}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-3 inline-flex items-center gap-1.5 text-xs font-semibold text-[#C13584] transition-opacity hover:opacity-75"
                      >
                        <svg viewBox="0 0 24 24" fill="currentColor" className="h-3.5 w-3.5" aria-hidden>
                          <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                        </svg>
                        Instagram
                      </a>
                    )}
                  </div>
                </div>

                <div>
                  <p className="text-[17px] font-semibold leading-8 text-[#1E293B]">
                    {founder.intro}
                  </p>

                  <div className="mt-5 space-y-4">
                    {founder.story.map((paragraph) => (
                      <p
                        key={paragraph}
                        className="text-base font-medium leading-7 text-[#475569]"
                      >
                        {paragraph}
                      </p>
                    ))}
                  </div>

                  <div className="mt-6 grid gap-5 sm:grid-cols-2">
                    <div className="rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] p-5 transition-all duration-300 hover:border-[#BAE6FD] hover:bg-white hover:shadow-[0_16px_30px_-24px_rgba(15,23,42,0.35)]">
                      <h4 className="text-sm font-bold uppercase tracking-[0.9px] text-[#0F172A]">
                        Key Outcomes
                      </h4>
                      <ul className="mt-3 space-y-2.5 text-sm font-medium leading-6 text-[#334155]">
                        {founder.outcomes.map((item) => (
                          <li key={item} className="flex gap-2.5">
                            <span className="text-[#0EA5E9]" aria-hidden>✓</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] p-5 transition-all duration-300 hover:border-[#BAE6FD] hover:bg-white hover:shadow-[0_16px_30px_-24px_rgba(15,23,42,0.35)]">
                      <h4 className="text-sm font-bold uppercase tracking-[0.9px] text-[#0F172A]">
                        How They Guide Aspirants
                      </h4>
                      <ul className="mt-3 space-y-2.5 text-sm font-medium leading-6 text-[#334155]">
                        {founder.focus.map((item) => (
                          <li key={item} className="flex gap-2.5">
                            <span className="text-[#0EA5E9]" aria-hidden>✓</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <blockquote className="mt-6 rounded-2xl border border-[#DBEAFE] bg-[#EFF6FF] p-5 text-base font-semibold leading-7 text-[#1E40AF] transition-all duration-300 hover:bg-[#E0F2FE]">
                    &quot;{founder.quote}&quot;
                  </blockquote>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* Philosophy + CTA */}
      <section className="border-y border-[#E2E8F0] bg-white">
        <div className="page-shell py-16 sm:py-20">
          <div className="rounded-[28px] border border-[#E2E8F0] bg-linear-to-b from-[#F8FBFF] to-sky-50 p-8 shadow-[0_24px_54px_-34px_rgba(14,116,144,0.25)] sm:p-12">
            <h2 className="text-center font-display text-3xl font-extrabold tracking-[-0.7px] text-[#0C1A3A] sm:text-4xl">
              DentNav Philosophy
            </h2>

            <ul className="mt-8 grid gap-3 sm:mt-10">
              {philosophy.map((item) => (
                <li
                  key={item}
                  className="flex items-start gap-3 rounded-xl border border-[#DBEAFE] bg-white px-4 py-3.5 text-[15px] font-medium leading-7 text-[#334155] transition-all duration-300 hover:-translate-y-0.5 hover:border-[#93C5FD] hover:shadow-[0_10px_24px_-20px_rgba(14,116,144,0.5)] sm:text-base"
                >
                  <span className="mt-1 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[#E0F2FE] text-xs font-bold text-[#0369A1]">
                    ✓
                  </span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>

            <p className="mt-8 text-center text-base font-medium leading-8 text-[#334155] sm:mt-10 sm:text-lg">
              Before you decide your future, talk to someone who has already
              walked the path.
            </p>
            <p className="mt-1 text-center text-base font-bold text-[#0C4A6E] sm:text-lg">
              Let DentNav guide you from confusion to clarity, from uncertainty
              to confidence.
            </p>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-3 sm:mt-10">
              <span className="relative inline-flex rounded-full">
                <span className="dentnav-cta-primary__halo rounded-full" aria-hidden />
                <Link
                  href="/questionnaire"
                  className="dentnav-cta-primary relative z-[1] inline-flex items-center justify-center rounded-full bg-[linear-gradient(99.11deg,#006591_0%,#0EA5E9_100%)] px-7 py-3 text-sm font-bold leading-5 text-white shadow-[0_10px_24px_-14px_rgba(0,101,145,0.8)] transition-all duration-300 hover:-translate-y-1 hover:brightness-110 active:scale-[0.98]"
                >
                  <span className="dentnav-cta-primary__shine" aria-hidden />
                  <span className="relative z-[1]">Start Your Guidance Plan</span>
                </Link>
              </span>
              {secondaryCta ?? (
                <Link
                  href="/auth/login"
                  className="inline-flex items-center justify-center rounded-full border border-[#BAE6FD] bg-white px-7 py-3 text-sm font-bold text-[#0C4A6E] transition-all hover:border-[#7DD3FC] hover:bg-[#F0F9FF]"
                >
                  Talk to DentNav
                </Link>
              )}
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
