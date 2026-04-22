import type { ReadinessDimension, ReadinessScore } from "@/lib/analysis.types";

type ReadinessScoreCardProps = {
  data: ReadinessScore;
};

type RatingTone = "strong" | "good" | "warn" | "gap";

const FALLBACK_HEADLINE = "Personalized readiness snapshot";

/**
 * Maps the LLM's freeform status string to a color tone.
 * Backend may also emit `statusColor` ("green" | "orange" | "red"); honor it
 * when present to keep server + client visuals aligned.
 */
function ratingTone(dim: ReadinessDimension): RatingTone {
  const explicit = dim.statusColor?.toLowerCase().trim();
  if (explicit === "green") return "strong";
  if (explicit === "orange" || explicit === "yellow" || explicit === "amber") return "warn";
  if (explicit === "red") return "gap";

  const status = dim.status.toLowerCase().trim();
  if (/(strong|excellent|met|meets|competitive|pass)/.test(status)) return "strong";
  if (/(good|on[- ]?track|solid)/.test(status)) return "good";
  if (/(unclear|partial|undecided|in ?progress|developing)/.test(status)) return "warn";
  if (/(gap|risk|missing|blocker|low|none|weak)/.test(status)) return "gap";

  if (dim.score >= 70) return "strong";
  if (dim.score >= 55) return "good";
  if (dim.score >= 35) return "warn";
  return "gap";
}

const TONE_BAR: Record<RatingTone, string> = {
  strong: "bg-emerald-500",
  good: "bg-emerald-500/85",
  warn: "bg-amber-500",
  gap: "bg-rose-500",
};

const TONE_LABEL: Record<RatingTone, string> = {
  strong: "text-emerald-700",
  good: "text-emerald-700/90",
  warn: "text-amber-700",
  gap: "text-rose-700",
};

const STRENGTH_PILL =
  "rounded-full bg-emerald-500/12 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-800 ring-1 ring-emerald-600/20";

const GAP_PILL =
  "rounded-full bg-rose-500/12 px-2.5 py-0.5 text-[11px] font-semibold text-rose-800 ring-1 ring-rose-600/20";

function clamp(n: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, n));
}

function HeadlineBar({ score, label }: { score: number; label: string }) {
  const pct = clamp(score, 0, 100);
  return (
    <div className="flex w-full items-center gap-5">
      <div className="flex shrink-0 flex-col items-start">
        <span className="font-display text-[44px] font-extrabold leading-none tracking-[-1.6px] text-[#0C1A3A] sm:text-[52px]">
          {Math.round(pct)}
        </span>
        <span className="mt-1 text-[10px] font-medium uppercase tracking-[1.3px] text-slate-500">
          out of 100
        </span>
      </div>
      <div className="flex min-w-0 flex-1 flex-col gap-2">
        <div className="relative h-2 w-full overflow-hidden rounded-full bg-slate-100 ring-1 ring-slate-200/80">
          <div
            className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-sky-500 to-emerald-500 transition-[width] duration-300 ease-out"
            style={{ width: `${pct}%` }}
          />
        </div>
        <p className="text-sm font-medium leading-5 text-[#3E4850]">
          {label || FALLBACK_HEADLINE}
        </p>
      </div>
    </div>
  );
}

function DimensionRow({ dim }: { dim: ReadinessDimension }) {
  const tone = ratingTone(dim);
  const pct = clamp(dim.score, 0, 100);
  return (
    <li className="grid grid-cols-[minmax(0,150px)_minmax(0,1fr)_auto] items-center gap-3 sm:gap-5">
      <span className="truncate text-[13px] font-medium text-[#0C1A3A]/85">{dim.name}</span>
      <div className="relative h-1.5 min-w-0 overflow-hidden rounded-full bg-slate-100 ring-1 ring-slate-200/80">
        <div
          className={`absolute inset-y-0 left-0 rounded-full ${TONE_BAR[tone]}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={`shrink-0 text-[13px] font-semibold ${TONE_LABEL[tone]}`}>{dim.status || "—"}</span>
    </li>
  );
}

export function ReadinessScoreCard({ data }: ReadinessScoreCardProps) {
  const dims = data.dimensions ?? [];
  const strengths = (data.strengths ?? []).filter((s) => s && s.trim().length);
  const gaps = (data.gaps ?? []).filter((g) => g && g.trim().length);

  return (
    <section className="relative z-[1] mx-auto w-full rounded-[32px] border border-sky-500/10 bg-white/[0.98] p-5 shadow-[0_25px_50px_-12px_rgba(0,0,0,0.25)] backdrop-blur-xl sm:p-7">
      <header className="mb-4 flex items-center justify-between gap-4">
        <p className="text-[11px] font-bold uppercase tracking-[2px] text-slate-500">
          Readiness Score — {dims.length || 6} Dimensions
        </p>
      </header>

      <HeadlineBar score={data.overall} label={data.status} />

      {dims.length > 0 ? (
        <ul className="mt-6 flex flex-col gap-2.5">
          {dims.map((dim, idx) => (
            <DimensionRow key={`${dim.name}-${idx}`} dim={dim} />
          ))}
        </ul>
      ) : (
        <p className="mt-6 text-sm text-slate-500">
          Per-dimension breakdown will appear here.
        </p>
      )}

      {(strengths.length > 0 || gaps.length > 0) ? (
        <div className="mt-6 grid gap-5 sm:grid-cols-2">
          {strengths.length > 0 ? (
            <div>
              <h3 className="text-[13px] font-semibold text-[#0C1A3A]">Strengths</h3>
              <ul className="mt-2 flex flex-wrap gap-1.5">
                {strengths.map((s, i) => (
                  <li key={`${s}-${i}`} className={STRENGTH_PILL}>
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
          {gaps.length > 0 ? (
            <div>
              <h3 className="text-[13px] font-semibold text-[#0C1A3A]">Gaps to close</h3>
              <ul className="mt-2 flex flex-wrap gap-1.5">
                {gaps.map((g, i) => (
                  <li key={`${g}-${i}`} className={GAP_PILL}>
                    {g}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
