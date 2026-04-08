import type { ReactNode } from "react";
import Link from "next/link";
import Cubes from "./Cubes";
import DotGrid from "./DotGrid";

function ProblemCard({
  icon,
  label,
}: {
  icon: ReactNode;
  label: string;
}) {
  return (
    <div className="flex min-h-[110px] min-w-[160px] flex-1 flex-col gap-3 rounded-xl border border-[#F1F5F9] bg-white p-4 shadow-[0_10px_30px_rgba(13,28,46,0.04)] transition-all hover:shadow-[0_15px_35px_rgba(13,28,46,0.08)]">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-50 text-slate-400">
        {icon}
      </div>
      <p className="text-sm font-semibold leading-[20px] text-[#334155]">
        {label}
      </p>
    </div>
  );
}

const floatAccent = {
  teal: {
    shell:
      "border border-teal-100/90 bg-gradient-to-br from-teal-50/95 via-white/90 to-cyan-50/40 shadow-[0_12px_28px_-8px_rgba(13,148,136,0.18)] backdrop-blur-sm",
    bar: "bg-teal-500",
    eyebrow: "text-teal-800/90",
    tag: "bg-teal-100/80 text-teal-900",
  },
  sky: {
    shell:
      "border border-sky-100/90 bg-gradient-to-br from-sky-50/95 via-white/90 to-sky-50/30 shadow-[0_12px_28px_-8px_rgba(14,165,233,0.2)] backdrop-blur-sm",
    bar: "bg-sky-500",
    eyebrow: "text-sky-800/90",
    tag: "bg-sky-100/80 text-sky-900",
  },
  violet: {
    shell:
      "border border-violet-100/90 bg-gradient-to-br from-violet-50/95 via-white/90 to-fuchsia-50/35 shadow-[0_12px_28px_-8px_rgba(124,58,237,0.15)] backdrop-blur-sm",
    bar: "bg-violet-500",
    eyebrow: "text-violet-900/85",
    tag: "bg-violet-100/80 text-violet-900",
  },
  amber: {
    shell:
      "border border-amber-100/90 bg-gradient-to-br from-amber-50/95 via-white/90 to-orange-50/35 shadow-[0_12px_28px_-8px_rgba(217,119,6,0.16)] backdrop-blur-sm",
    bar: "bg-amber-500",
    eyebrow: "text-amber-900/85",
    tag: "bg-amber-100/85 text-amber-950",
  },
  emerald: {
    shell:
      "border border-emerald-100/90 bg-gradient-to-br from-emerald-50/95 via-white/90 to-teal-50/30 shadow-[0_12px_28px_-8px_rgba(5,150,105,0.16)] backdrop-blur-sm",
    bar: "bg-emerald-500",
    eyebrow: "text-emerald-900/85",
    tag: "bg-emerald-100/80 text-emerald-950",
  },
} as const;

type FloatAccent = keyof typeof floatAccent;

const floatIconTint: Record<FloatAccent, string> = {
  sky: "text-sky-600",
  teal: "text-teal-600",
  violet: "text-violet-600",
  amber: "text-amber-600",
  emerald: "text-emerald-600",
};

function HeroFloatCard({
  icon,
  eyebrow,
  title,
  description,
  tags,
  align = "left",
  iconAlign = "left",
  accent = "sky",
  className,
}: {
  icon: ReactNode;
  eyebrow: string;
  title: string;
  description?: string;
  tags?: string[];
  align?: "left" | "right" | "center";
  /** Icon + tags row: visa card uses `right` so the icon sits on the right with tags to its left. */
  iconAlign?: "left" | "right";
  accent?: FloatAccent;
  className?: string;
}) {
  const a = floatAccent[accent];
  const alignCls =
    align === "right" ? "text-right" : align === "center" ? "text-center" : "";

  const rowDir = align === "right" ? "flex-row-reverse" : "flex-row";

  const iconEl = (
    <span
      className={`inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/95 shadow-sm ring-1 ring-slate-200/90 [&_svg]:h-5 [&_svg]:w-5 ${floatIconTint[accent]}`}
      aria-hidden
    >
      {icon}
    </span>
  );

  const tagEls =
    tags && tags.length > 0
      ? tags.map((t) => (
          <span
            key={t}
            className={`rounded-full px-2 py-0.5 font-display text-[10px] font-semibold leading-[15px] ${a.tag}`}
          >
            {t}
          </span>
        ))
      : null;

  const iconTagsRow = (
    <div
      className={`mt-2.5 flex flex-row flex-wrap items-center gap-2 ${iconAlign === "right" ? "justify-end" : "justify-start"}`}
    >
      {iconAlign === "right" ? (
        <>
          {tagEls}
          {iconEl}
        </>
      ) : (
        <>
          {iconEl}
          {tagEls}
        </>
      )}
    </div>
  );

  return (
    <div
      className={`flex max-w-[min(280px,100%)] gap-3 rounded-2xl px-4 py-4 ${rowDir} ${a.shell} ${alignCls} ${className}`}
    >
      <span
        className={`mt-0.5 w-1 shrink-0 self-stretch rounded-full ${a.bar}`}
        aria-hidden
      />
      <div className="min-w-0 flex-1">
        <p className={`font-display text-[10px] font-bold uppercase leading-4 tracking-[0.45px] ${a.eyebrow}`}>
          {eyebrow}
        </p>
        <p className="mt-0.5 font-display text-sm font-bold leading-snug text-dent-ink">{title}</p>
        {description ? (
          <div className="mt-1 space-y-0">
            {description
              .split("\n")
              .map((line) => line.trim())
              .filter(Boolean)
              .map((line, i) => (
                <p key={i} className="text-xs font-normal leading-[17px] text-[#475569]">
                  {line}
                </p>
              ))}
          </div>
        ) : null}
        {iconTagsRow}
      </div>
    </div>
  );
}

export function HeroSection() {
  return (
    <section className="relative isolate min-h-0 overflow-hidden bg-white pb-2.5 pt-[78px] lg:min-h-[1024px] lg:pb-2.5">
      {/* Interactive dot grid background */}
      <div className="pointer-events-auto absolute inset-0 z-0" aria-hidden>
        <DotGrid
          dotSize={4}
          gap={18}
          baseColor="#E2E8F0"
          activeColor="#0EA5E9"
          proximity={88}
          speedTrigger={320}
          maxSpeed={1800}
          cursorPushScale={0.28}
          shockRadius={180}
          shockStrength={3}
          resistance={750}
          returnDuration={1}
        />
      </div>

      <div
        className="pointer-events-none absolute left-1/2 top-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[rgba(14,165,233,0.06)] blur-[80px]"
        aria-hidden
      />

      {/* Figma: hero content left:48 right:770 → 622px text; illustration left:770 → 806px */}
      <div className="relative z-[2] page-shell">
        <div className="grid w-full items-start gap-12 lg:grid-cols-[minmax(0,622px)_minmax(0,1fr)] lg:items-stretch lg:gap-x-[100px]">
          <div className="max-w-[622px] lg:pt-[67px]">
            <p className="inline-flex items-center rounded-full border border-[rgba(14,165,233,0.2)] bg-dent-badge-bg px-4 py-1.5 text-xs font-bold uppercase leading-4 tracking-[0.3px] text-dent-deep">
              Navigate U.S. dentistry with confidence
            </p>

            <div className="pt-8">
              <h1 className="max-w-[620px] font-display text-xl font-bold leading-[1.09] tracking-[-1.2px] text-dent-ink sm:text-xl lg:text-[64px] lg:leading-[70px]">
                Your Journey to Practicing{" "}
                <span className="text-dent-sky">Dentistry</span> in the United States Starts Here
              </h1>
            </div>

            <div className="max-w-[600px] pt-8">
              <p className="text-xl font-normal leading-7 text-[#475569]">
                DentNav helps foreign-trained dentists navigate the complex pathway to U.S. dental careers with clarity,strategy and confidence.
              </p>
            </div>

            <div className="w-full max-w-[622px] pt-8">
              <div className="flex flex-col gap-6 pt-4">
                <div className="flex flex-col gap-4 sm:flex-row">
                  <ProblemCard
                    label="CAAPID, PASS & other applications"
                    icon={
                      <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" aria-hidden>
                        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    }
                  />
                  <ProblemCard
                    label="Expert Bench Prep & Training"
                    icon={
                      <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" aria-hidden>
                        <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 11-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.77 3.77z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    }
                  />
                  <ProblemCard
                    label="INBDE WORLD Coming Soon.."
                    icon={
                      <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" aria-hidden>
                        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
                        <path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10M12 2a15.3 15.3 0 00-4 10 15.3 15.3 0 004 10" stroke="currentColor" strokeWidth="2" />
                      </svg>
                    }
                  />
                </div>

                <p className="flex items-center gap-2 text-sm font-medium leading-5 text-dent-deep">
                  You're not alone - and you don't have to figure it out by yourself.
                </p>
              </div>
            </div>

            <div className="max-w-[530px] pt-8">
              <div className="flex flex-col gap-[11px] pt-4">
              <span className="relative inline-flex w-full rounded-full">
                  <span className="dentnav-cta-primary__halo rounded-full" aria-hidden />
                  <Link
                    href="/questionnaire"
                    className="dentnav-cta-primary group relative z-[1] inline-flex w-full items-center justify-center gap-2 rounded-full bg-[linear-gradient(98.5deg,#006591_0%,#0EA5E9_100%)] px-8 py-5 text-lg font-bold leading-7 text-white transition-all duration-300 hover:-translate-y-1 hover:brightness-110 active:scale-[0.98]"
                  >
                    <span className="dentnav-cta-primary__shine" aria-hidden />
                    <span className="relative z-[1]">Start Your Journey Today</span>
                    <span
                      className="relative z-[1] transition-transform duration-300 group-hover:translate-x-1"
                      aria-hidden
                    >
                      →
                    </span>
                  </Link>
                </span>
                <p className="px-20 text-[13px] font-normal leading-5 text-[#94A3B8]">
                  Answer a quick questionnaire to know where you stand
                </p>
              </div>
            </div>
          </div>

          <div className="relative z-[2] flex left-[8%] h-full min-h-[min(520px,78vh)] w-full max-w-[min(100%,920px)] items-center justify-center self-stretch px-1 py-8 sm:px-2 lg:min-h-[min(640px,82vh)] lg:min-h-0 lg:-translate-y-6 lg:py-0">
            <Cubes
              className="cubes--hero"
              gridCols={6}
              gridRows={8}
              faceRadius={3.5}
              maxAngle={35}
              radius={2.5}
              borderStyle="1px solid rgba(14, 165, 233, 0.28)"
              faceColor="#eff6ff"
              rippleColor="#38bdf8"
              rippleSpeed={1.5}
              autoAnimate
              rippleOnClick
            />
          </div>
        </div>

        {/* 4 info cards in the open hero zones — pointer-events-none keeps cubes/links usable */}
        <div
          className="pointer-events-none absolute inset-x-0 bottom-0 top-0 z-[5] hidden lg:block"
          aria-hidden
        >
          {/* 1 — top of the gap between left column and cube */}
          <HeroFloatCard
            accent="sky"
            icon={
              <svg viewBox="0 0 24 24" fill="none" aria-hidden>
                <path
                  d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"
                  stroke="currentColor"
                  strokeWidth="1.75"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M14 2v6h6M16 13H8M16 17H8M10 9H8"
                  stroke="currentColor"
                  strokeWidth="1.75"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            }
            eyebrow="Application cycle"
            title="CAAPID & programs"
            description={
              "Strong applications and school enrollments.\nTimelines that match your goals."
            }
            tags={["CAAPID", "SOPs", "LORs"]}
            className="absolute left-[45%] top-[2%] max-w-[min(310px,30vw)]"
          />

          {/* 2 — top right; card centre ≈ cube's right edge */}
          <HeroFloatCard
            accent="teal"
            align="right"
            iconAlign="right"
            icon={
              <svg viewBox="0 0 24 24" fill="none" aria-hidden>
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.75" />
                <path
                  d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10M12 2a15.3 15.3 0 00-4 10 15.3 15.3 0 004 10"
                  stroke="currentColor"
                  strokeWidth="1.75"
                />
              </svg>
            }
            eyebrow="Visa & status"
            title="Immigration pathways"
            description={
              "Common visa paths for dentists.\nPlan status before you move."
            }
            tags={["EB1", "O1", "H1B", "F1", "J1"]}
            className="absolute right-[2%] top-[-2%] max-w-[min(280px,25vw)]"
          />

          {/* 3 — vertically centred in the column gap */}
          <HeroFloatCard
            accent="violet"
            icon={
              <svg viewBox="0 0 24 24" fill="none" aria-hidden>
                <path
                  d="M22 10v6M2 10l10-5 10 5-10 5z"
                  stroke="currentColor"
                  strokeWidth="1.75"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M6 12v5c3 3 9 3 12 0v-5"
                  stroke="currentColor"
                  strokeWidth="1.75"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            }
            eyebrow="Education tracks"
            title="Advanced Standing DDS"
            description={
              "AS-DDS, GPR, and AEGD compared.\nPick what fits your timeline."
            }
            tags={["AS-DDS", "GPR", "AEGD"]}
            className="absolute left-[51%] top-[52%] max-w-[min(310px,25vw)] -translate-y-1/2"
          />

          {/* 4 — below the cube */}
          <HeroFloatCard
            accent="amber"
            align="center"
            icon={
              <svg viewBox="0 0 24 24" fill="none" aria-hidden>
                <path
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                  stroke="currentColor"
                  strokeWidth="1.75"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            }
            eyebrow="Exams & licensure"
            title="INBDE → State License"
            description={
              "INBDE through bench tests to licensure.\nEach step in order."
            }
            tags={["INBDE", "Bench tests", "State Boards"]}
            className="absolute bottom-[1%] left-[72%] max-w-[min(330px,35vw)]"
          />
        </div>
      </div>
    </section>
  );
}
