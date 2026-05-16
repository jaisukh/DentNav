"use client";

import Image from "next/image";
import type {
  AnalysisFullPayload,
  MainRisk,
  MythWarning,
  RankedPathway,
  StateInfo,
  TimelineMilestone,
} from "@/lib/analysis-full.types";

// ─── Color helpers ────────────────────────────────────────────────────────────

function scoreColors(score: number) {
  if (score >= 80) return { stroke: "#10b981", textClass: "text-emerald-400" };
  if (score >= 60) return { stroke: "#14b8a6", textClass: "text-teal-400" };
  if (score >= 40) return { stroke: "#f59e0b", textClass: "text-amber-400" };
  return { stroke: "#f43f5e", textClass: "text-rose-400" };
}

function statusColorClasses(statusColor?: string) {
  switch (statusColor?.toLowerCase()) {
    case "green":
      return { bar: "bg-emerald-500", badge: "bg-emerald-50 text-emerald-700 border-emerald-200" };
    case "teal":
      return { bar: "bg-teal-500", badge: "bg-teal-50 text-teal-700 border-teal-200" };
    case "amber":
      return { bar: "bg-amber-400", badge: "bg-amber-50 text-amber-700 border-amber-200" };
    case "red":
      return { bar: "bg-rose-500", badge: "bg-rose-50 text-rose-700 border-rose-200" };
    default:
      return { bar: "bg-slate-400", badge: "bg-slate-50 text-slate-600 border-slate-200" };
  }
}

function impactColorClasses(color: string) {
  switch (color?.toLowerCase()) {
    case "red":  return "bg-rose-100 text-rose-700 border-rose-200";
    case "amber": return "bg-amber-100 text-amber-700 border-amber-200";
    case "green": return "bg-emerald-100 text-emerald-700 border-emerald-200";
    default:     return "bg-slate-100 text-slate-600 border-slate-200";
  }
}

function periodColorClasses(periodColor: string) {
  switch (periodColor?.toLowerCase()) {
    case "red":    return { dot: "bg-rose-500",    ring: "ring-rose-100",    pill: "bg-rose-100 text-rose-700" };
    case "amber":  return { dot: "bg-amber-500",   ring: "ring-amber-100",   pill: "bg-amber-100 text-amber-700" };
    case "purple": return { dot: "bg-purple-500",  ring: "ring-purple-100",  pill: "bg-purple-100 text-purple-700" };
    case "teal":   return { dot: "bg-teal-500",    ring: "ring-teal-100",    pill: "bg-teal-100 text-teal-700" };
    case "green":  return { dot: "bg-emerald-500", ring: "ring-emerald-100", pill: "bg-emerald-100 text-emerald-700" };
    default:       return { dot: "bg-slate-400",   ring: "ring-slate-100",   pill: "bg-slate-100 text-slate-600" };
  }
}

// ─── Score Gauge (SVG arc) ────────────────────────────────────────────────────

function ScoreGauge({ score, size = 144 }: { score: number; size?: number }) {
  const r = (size - 20) / 2;
  const cx = size / 2;
  const cy = size / 2;
  const circumference = 2 * Math.PI * r;
  const filled = (score / 100) * circumference;
  const { stroke, textClass } = scoreColors(score);

  return (
    <div className="relative flex items-center justify-center shrink-0" style={{ width: size, height: size }}>
      <svg className="absolute inset-0 -rotate-90" width={size} height={size} aria-hidden>
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth="11" />
        <circle
          cx={cx} cy={cy} r={r} fill="none"
          stroke={stroke} strokeWidth="11"
          strokeDasharray={`${filled} ${circumference - filled}`}
          strokeLinecap="round"
        />
      </svg>
      <div className="relative flex flex-col items-center select-none">
        <span className={`text-[2.25rem] font-extrabold leading-none tracking-tight ${textClass}`}>{score}</span>
        <span className="mt-1 text-[10px] font-bold uppercase tracking-widest text-white/40">/ 100</span>
      </div>
    </div>
  );
}

// ─── Section header ────────────────────────────────────────────────────────────

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <div className="mb-5 flex items-center gap-3">
      <span className="h-5 w-1 shrink-0 rounded-full bg-sky-500" />
      <h2 className="font-display text-[15px] font-extrabold tracking-tight text-slate-900">{children}</h2>
    </div>
  );
}

// ─── Readiness dimension bar ───────────────────────────────────────────────────

function DimensionBar({
  name, score, status, statusColor,
}: {
  name: string; score: number; status: string; statusColor?: string;
}) {
  const { bar, badge } = statusColorClasses(statusColor);
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between gap-2">
        <span className="font-display text-sm font-medium leading-5 text-slate-700">{name}</span>
        <span className={`shrink-0 rounded-full border px-2.5 py-0.5 text-[11px] font-bold ${badge}`}>{status}</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full rounded-full transition-all ${bar}`} style={{ width: `${score}%` }} />
      </div>
    </div>
  );
}

// ─── Risk card ─────────────────────────────────────────────────────────────────

function RiskCard({ risk }: { risk: MainRisk }) {
  const badge = impactColorClasses(risk.impactColor);
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-2 flex items-start justify-between gap-3">
        <span className="font-display text-sm font-bold text-slate-900">{risk.issue}</span>
        <span className={`shrink-0 rounded-full border px-2.5 py-0.5 text-[11px] font-bold ${badge}`}>{risk.impact}</span>
      </div>
      <p className="font-display text-sm leading-5 text-slate-600">{risk.note}</p>
      <p className="mt-2 font-display text-xs italic text-slate-400">Basis: {risk.evidenceBasis}</p>
    </div>
  );
}

// ─── Ranked pathway card ───────────────────────────────────────────────────────

function PathwayCard({ pathway }: { pathway: RankedPathway }) {
  return (
    <div className={`rounded-xl border p-5 ${pathway.isPrimary ? "border-sky-300 bg-sky-50/50" : "border-slate-200 bg-white"}`}>
      <div className="mb-2 flex items-start gap-2.5">
        <span className={`mt-0.5 shrink-0 rounded-full px-2 py-0.5 text-[11px] font-extrabold ${pathway.isPrimary ? "bg-sky-500 text-white" : "bg-slate-100 text-slate-500"}`}>
          {pathway.rankLabel}
        </span>
        <span className="font-display text-sm font-bold text-slate-900">{pathway.pathTitle}</span>
      </div>
      <p className="font-display text-sm leading-5 text-slate-600">{pathway.fitSummary}</p>
      {pathway.blockers.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {pathway.blockers.map((b) => (
            <span key={b} className="rounded-full border border-rose-200 bg-rose-50 px-2 py-0.5 text-[11px] font-medium text-rose-600">{b}</span>
          ))}
        </div>
      )}
      {pathway.realityCheck && (
        <p className="mt-3 font-display text-xs italic text-slate-400">{pathway.realityCheck}</p>
      )}
      {pathway.isPrimary && pathway.applicationPortal && (
        <p className="mt-2 font-display text-xs font-medium text-sky-600">Portal: {pathway.applicationPortal}</p>
      )}
    </div>
  );
}

// ─── Timeline item ─────────────────────────────────────────────────────────────

function TimelineItem({ item, isLast }: { item: TimelineMilestone; isLast: boolean }) {
  const { dot, ring, pill } = periodColorClasses(item.periodColor);
  return (
    <div className="flex gap-4">
      <div className="flex shrink-0 flex-col items-center">
        <div className={`mt-1 h-3 w-3 rounded-full ring-4 ring-offset-1 ${dot} ${ring}`} />
        {!isLast && <div className="mt-1 min-h-[40px] flex-1 w-px bg-slate-200" />}
      </div>
      <div className="pb-7">
        <span className={`mb-1.5 inline-block rounded-full px-2.5 py-0.5 text-[11px] font-bold ${pill}`}>{item.period}</span>
        <h4 className="font-display text-sm font-bold text-slate-900">{item.milestone}</h4>
        <p className="mt-1 font-display text-sm leading-5 text-slate-500">{item.detail}</p>
      </div>
    </div>
  );
}

// ─── State card ────────────────────────────────────────────────────────────────

function StateCard({ state }: { state: StateInfo }) {
  const compLower = state.competitiveness?.toLowerCase() ?? "";
  const compBadge = compLower.includes("high")
    ? "border-rose-200 bg-rose-50 text-rose-700"
    : compLower.includes("moderate")
    ? "border-amber-200 bg-amber-50 text-amber-700"
    : "border-teal-200 bg-teal-50 text-teal-700";

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h4 className="font-display text-base font-extrabold text-slate-900">{state.name}</h4>
        <span className={`shrink-0 rounded-full border px-2.5 py-0.5 text-[11px] font-bold ${compBadge}`}>{state.competitiveness}</span>
      </div>
      <p className="font-display text-sm leading-5 text-slate-600">{state.notes}</p>
      {state.priorityActions.length > 0 && (
        <div className="mt-3">
          <p className="mb-2 font-display text-[11px] font-bold uppercase tracking-wider text-slate-400">Priority Actions</p>
          <ul className="flex flex-col gap-1.5">
            {state.priorityActions.map((a) => (
              <li key={a} className="flex items-start gap-2 font-display text-sm text-slate-600">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-sky-400" />
                {a}
              </li>
            ))}
          </ul>
        </div>
      )}
      {state.riskFlags.length > 0 && (
        <div className="mt-3 flex flex-col gap-1">
          {state.riskFlags.map((f) => (
            <p key={f} className="font-display text-xs italic text-rose-500">{f}</p>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Myth / Reality card ───────────────────────────────────────────────────────

function MythCard({ myth }: { myth: MythWarning }) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 shadow-sm">
      <div className="flex items-start gap-3 border-b border-rose-100 bg-rose-50 px-5 py-3.5">
        <svg width="16" height="16" viewBox="0 0 20 20" fill="none" className="mt-0.5 shrink-0" aria-hidden>
          <path fillRule="evenodd" clipRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" fill="#f43f5e" />
        </svg>
        <div>
          <p className="mb-0.5 font-display text-[11px] font-bold uppercase tracking-wider text-rose-500">Myth</p>
          <p className="font-display text-sm font-medium leading-5 text-rose-900">{myth.myth}</p>
        </div>
      </div>
      <div className="flex items-start gap-3 bg-emerald-50 px-5 py-3.5">
        <svg width="16" height="16" viewBox="0 0 20 20" fill="none" className="mt-0.5 shrink-0" aria-hidden>
          <path fillRule="evenodd" clipRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" fill="#10b981" />
        </svg>
        <div>
          <p className="mb-0.5 font-display text-[11px] font-bold uppercase tracking-wider text-emerald-600">Reality</p>
          <p className="font-display text-sm font-medium leading-5 text-emerald-900">{myth.fact}</p>
        </div>
      </div>
    </div>
  );
}

// ─── Main component ────────────────────────────────────────────────────────────

export function FullAnalysisView({ data }: { data: AnalysisFullPayload }) {
  const {
    readinessScore,
    profileSnapshot,
    pathwayRecommendation,
    mainRisks,
    next90DaysPlan,
    next12To18Months,
    dentnavServices,
    applicationTimeline,
    mythWarnings,
    statePlanning,
    expertConclusion,
  } = data;

  const score = readinessScore?.overall ?? 0;

  const profilePills = [
    profileSnapshot?.country,
    profileSnapshot?.degree,
    profileSnapshot?.clinicalExperience,
    profileSnapshot?.targetCycle ? `Target: ${profileSnapshot.targetCycle}` : null,
  ].filter((v): v is string => Boolean(v));

  const generatedDate = new Date().toLocaleDateString("en-US", { month: "long", year: "numeric" });

  return (
    <div className="w-full pb-16 font-display text-slate-900">

      {/* ── Hero ── */}
      <div className="relative mb-6 overflow-hidden rounded-2xl bg-gradient-to-br from-[#001220] via-[#001E2F] to-[#003751] px-6 py-8 sm:px-10">
        {/* ambient glow */}
        <div
          className="pointer-events-none absolute -top-24 right-0 h-[320px] w-[320px] rounded-full bg-sky-500/10 blur-3xl"
          aria-hidden
        />
        <div className="relative z-10 flex flex-col gap-8 sm:flex-row sm:items-center sm:justify-between">

          {/* Left: branding + profile */}
          <div className="flex flex-col gap-5">
            {/* DentNav wordmark */}
            <div className="flex items-center gap-2.5">
              <Image src="/logo-white.png" alt="" width={36} height={36} className="shrink-0 object-contain" />
              <span className="text-xl font-bold tracking-tight text-white">DentNav</span>
              <span className="ml-1 rounded-full bg-sky-500/20 px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wider text-sky-300">
                Pathway Report
              </span>
            </div>

            {/* Title */}
            <div>
              <h1 className="text-2xl font-extrabold leading-tight tracking-tight text-white sm:text-3xl">
                Your U.S. Dentistry<br className="hidden sm:block" /> Pathway Analysis
              </h1>
              <p className="mt-1.5 text-sm font-medium text-sky-200/60">
                Personalised for your profile · {generatedDate}
              </p>
            </div>

            {/* Profile pills */}
            {profilePills.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {profilePills.map((p) => (
                  <span
                    key={p}
                    className="rounded-full border border-white/15 bg-white/8 px-3 py-1 text-xs font-semibold text-sky-100 backdrop-blur-sm"
                  >
                    {p}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Right: score gauge */}
          <div className="flex flex-col items-center gap-3 shrink-0">
            <ScoreGauge score={score} size={148} />
            <div className="text-center">
              <p className="text-xs font-bold uppercase tracking-widest text-white/40">Readiness Score</p>
              <p className="mt-1 max-w-[160px] text-center text-[13px] font-semibold leading-4 text-white/70">
                {readinessScore?.status}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* ── Expert Conclusion ── */}
      {expertConclusion && (
        <div className="mb-6 rounded-2xl border border-sky-200 bg-gradient-to-r from-sky-50/70 to-white px-6 py-5">
          <div className="flex items-start gap-4">
            <svg
              width="28" height="24" viewBox="0 0 28 24" fill="none"
              className="mt-0.5 shrink-0 opacity-20" aria-hidden
            >
              <path d="M0 24V14.727C0 12.758.348 10.909 1.045 9.182 1.742 7.455 2.697 5.909 3.91 4.545 5.121 3.182 6.545 2.06 8.182 1.182 9.818.303 11.576-.06 13.455.009L14.546 3.272c-1.334.486-2.516 1.091-3.546 1.818-1.03.727-1.909 1.576-2.636 2.546-.727.97-1.273 2.03-1.637 3.182C6.364 11.97 6.182 13.212 6.182 14.545V16H12V24H0zm16 0V14.727c0-1.969.348-3.818 1.045-5.545.697-1.727 1.652-3.273 2.865-4.637 1.212-1.363 2.636-2.484 4.273-3.363C25.818.303 27.576-.06 29.455.009L30.546 3.272c-1.334.486-2.516 1.091-3.546 1.818-1.03.727-1.909 1.576-2.636 2.546-.727.97-1.273 2.03-1.637 3.182-.363 1.152-.545 2.394-.545 3.727V16H28V24H16z" fill="#0EA5E9" />
            </svg>
            <p className="font-display text-[15px] leading-7 text-slate-700 italic">{expertConclusion}</p>
          </div>
        </div>
      )}

      <div className="flex flex-col gap-5">

        {/* ── Readiness Breakdown ── */}
        {readinessScore && (
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <SectionHeading>Readiness Breakdown</SectionHeading>
            <div className="flex flex-col gap-4">
              {readinessScore.dimensions?.map((d) => (
                <DimensionBar key={d.name} {...d} />
              ))}
            </div>
            <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2">
              {/* Strengths */}
              {readinessScore.strengths?.length > 0 && (
                <div>
                  <p className="mb-2.5 font-display text-[11px] font-bold uppercase tracking-wider text-emerald-600">Strengths</p>
                  <ul className="flex flex-col gap-2">
                    {readinessScore.strengths.map((s) => (
                      <li key={s} className="flex items-start gap-2 font-display text-sm text-slate-600">
                        <svg width="16" height="16" viewBox="0 0 20 20" fill="none" className="mt-0.5 shrink-0" aria-hidden>
                          <path fillRule="evenodd" clipRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" fill="#10b981" />
                        </svg>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {/* Gaps */}
              {readinessScore.gaps?.length > 0 && (
                <div>
                  <p className="mb-2.5 font-display text-[11px] font-bold uppercase tracking-wider text-rose-600">Gaps to Address</p>
                  <ul className="flex flex-col gap-2">
                    {readinessScore.gaps.map((g) => (
                      <li key={g} className="flex items-start gap-2 font-display text-sm text-slate-600">
                        <svg width="16" height="16" viewBox="0 0 20 20" fill="none" className="mt-0.5 shrink-0" aria-hidden>
                          <path fillRule="evenodd" clipRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" fill="#f43f5e" />
                        </svg>
                        {g}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── Pathway Recommendation ── */}
        {pathwayRecommendation && (
          <div className="rounded-2xl border border-sky-200 bg-gradient-to-b from-sky-50/50 to-white p-6 shadow-sm">
            <SectionHeading>Recommended Pathway</SectionHeading>

            {/* Primary pathway hero block */}
            <div className="mb-5 rounded-xl bg-sky-500 px-5 py-5 text-white">
              <p className="mb-1 font-display text-[11px] font-bold uppercase tracking-widest text-sky-200">
                Primary Recommendation
              </p>
              <h3 className="font-display text-lg font-extrabold leading-snug tracking-tight">
                {pathwayRecommendation.bestPathwayForYou}
              </h3>
              <p className="mt-2 font-display text-sm leading-6 text-sky-100">{pathwayRecommendation.verdict}</p>
            </div>

            {/* Why this fits */}
            {pathwayRecommendation.whyThisFits?.length > 0 && (
              <div className="mb-4">
                <p className="mb-2 font-display text-[11px] font-bold uppercase tracking-wider text-sky-600">Why this fits you</p>
                <ul className="flex flex-col gap-2">
                  {pathwayRecommendation.whyThisFits.map((w) => (
                    <li key={w} className="flex items-start gap-2 font-display text-sm text-slate-600">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-sky-400" />
                      {w}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Decision note */}
            {pathwayRecommendation.decisionNote && (
              <div className="mb-5 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3">
                <p className="mb-1 font-display text-[11px] font-bold uppercase tracking-wider text-amber-600">Decision Note</p>
                <p className="font-display text-sm leading-5 text-amber-900">{pathwayRecommendation.decisionNote}</p>
              </div>
            )}

            {/* Flip conditions */}
            {pathwayRecommendation.flipConditions?.length > 0 && (
              <div className="mb-5 rounded-lg border border-slate-100 bg-slate-50 px-4 py-3">
                <p className="mb-2 font-display text-[11px] font-bold uppercase tracking-wider text-slate-400">When This Could Change</p>
                <ul className="flex flex-col gap-1.5">
                  {pathwayRecommendation.flipConditions.map((fc) => (
                    <li key={fc} className="flex items-start gap-2 font-display text-sm text-slate-600">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-300" />
                      {fc}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Ranked pathways */}
            {pathwayRecommendation.rankedPathways?.length > 0 && (
              <div>
                <p className="mb-3 font-display text-[11px] font-bold uppercase tracking-wider text-slate-400">All Ranked Pathways</p>
                <div className="flex flex-col gap-3">
                  {pathwayRecommendation.rankedPathways.map((p) => (
                    <PathwayCard key={p.rank} pathway={p} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── Key Risks ── */}
        {mainRisks?.length > 0 && (
          <div className="rounded-2xl border border-rose-100 bg-white p-6 shadow-sm">
            <SectionHeading>Key Risks &amp; Blockers</SectionHeading>
            <div className="flex flex-col gap-3">
              {mainRisks.map((r) => (
                <RiskCard key={r.issue} risk={r} />
              ))}
            </div>
          </div>
        )}

        {/* ── Application Timeline ── */}
        {applicationTimeline?.length > 0 && (
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <SectionHeading>Application Timeline</SectionHeading>
            <div className="flex flex-col pt-1">
              {applicationTimeline.map((item, i) => (
                <TimelineItem key={item.period} item={item} isLast={i === applicationTimeline.length - 1} />
              ))}
            </div>
          </div>
        )}

        {/* ── Action Plans (2-col) ── */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          {next90DaysPlan?.length > 0 && (
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <SectionHeading>90-Day Action Plan</SectionHeading>
              <ol className="flex flex-col gap-3">
                {next90DaysPlan.map((item, i) => (
                  <li key={i} className="flex items-start gap-3 font-display text-sm text-slate-600">
                    <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-sky-100 text-[11px] font-extrabold text-sky-700">
                      {i + 1}
                    </span>
                    {item}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {next12To18Months?.length > 0 && (
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <SectionHeading>12–18 Month Milestones</SectionHeading>
              <ol className="flex flex-col gap-3">
                {next12To18Months.map((item, i) => (
                  <li key={i} className="flex items-start gap-3 font-display text-sm text-slate-600">
                    <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-purple-100 text-[11px] font-extrabold text-purple-700">
                      {i + 1}
                    </span>
                    {item}
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>

        {/* ── DentNav Services ── */}
        {(dentnavServices?.neededNow?.length > 0 || dentnavServices?.neededLater?.length > 0) && (
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <SectionHeading>DentNav Services for You</SectionHeading>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              {dentnavServices.neededNow?.length > 0 && (
                <div>
                  <span className="mb-3 inline-block rounded-full bg-rose-100 px-2.5 py-0.5 font-display text-[11px] font-bold text-rose-700">
                    Needed Now
                  </span>
                  <div className="flex flex-col gap-2.5">
                    {dentnavServices.neededNow.map((s) => (
                      <div key={s.service} className="rounded-lg border border-rose-100 bg-rose-50/40 px-4 py-3">
                        <p className="font-display text-sm font-bold text-slate-900">{s.service}</p>
                        <p className="mt-0.5 font-display text-xs text-slate-500">{s.reason}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {dentnavServices.neededLater?.length > 0 && (
                <div>
                  <span className="mb-3 inline-block rounded-full bg-sky-100 px-2.5 py-0.5 font-display text-[11px] font-bold text-sky-700">
                    Planned Later
                  </span>
                  <div className="flex flex-col gap-2.5">
                    {dentnavServices.neededLater.map((s) => (
                      <div key={s.service} className="rounded-lg border border-sky-100 bg-sky-50/40 px-4 py-3">
                        <p className="font-display text-sm font-bold text-slate-900">{s.service}</p>
                        <p className="mt-0.5 font-display text-xs text-slate-500">{s.reason}</p>
                        {s.timing && (
                          <p className="mt-1 font-display text-xs font-medium text-sky-600">{s.timing}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── State Planning ── */}
        {statePlanning?.states?.length > 0 && (
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <SectionHeading>State-by-State Planning</SectionHeading>
            {statePlanning.note && (
              <p className="mb-4 font-display text-sm text-slate-500">{statePlanning.note}</p>
            )}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {statePlanning.states.map((s) => (
                <StateCard key={s.name} state={s} />
              ))}
            </div>
          </div>
        )}

        {/* ── Myth Busters ── */}
        {mythWarnings?.length > 0 && (
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <SectionHeading>Common Myths — Busted</SectionHeading>
            <div className="flex flex-col gap-4">
              {mythWarnings.map((m) => (
                <MythCard key={m.myth} myth={m} />
              ))}
            </div>
          </div>
        )}

        {/* ── Footer branding ── */}
        <div className="flex flex-col items-center justify-between gap-4 rounded-2xl bg-[#001220] px-6 py-5 sm:flex-row">
          <div className="flex items-center gap-2.5">
            <Image src="/logo-white.png" alt="" width={28} height={28} className="shrink-0 object-contain" />
            <span className="font-display text-base font-bold tracking-tight text-white">DentNav</span>
          </div>
          <p className="max-w-sm text-center font-display text-xs leading-4 text-white/35 sm:text-right">
            This report is personalised to your questionnaire responses. Book a consultation with a DentNav counsellor to refine your strategy.
          </p>
        </div>
      </div>
    </div>
  );
}
