import { readinessLabel } from "@/lib/analysis-readiness";
import type { AnalysisResultPayload } from "@/lib/analysis.types";
import { ScoreGauge } from "./ScoreGauge";

type AnalysisResultsCardProps = {
  data: AnalysisResultPayload;
};

export function AnalysisResultsCard({ data }: AnalysisResultsCardProps) {
  const badge = readinessLabel(data.Performance);

  return (
    <section className="relative z-[1] top-[45px] mx-auto w-full max-w-[1136px] rounded-[32px] bg-white p-12 shadow-[0_20px_50px_rgba(14,165,233,0.12)]">
      <div className="flex flex-col gap-10 lg:flex-row lg:items-stretch lg:gap-0">
        {/* Score Gauge — Figma: left column ~30% (314.67 / 1040), border-right, pr-8 */}
        <div className="flex flex-col items-center border-slate-100 lg:w-[30%] lg:border-r lg:pr-8">
          <ScoreGauge value={data.Performance} />
          <div className="mt-6">
            <span className="font-display inline-flex rounded-full bg-emerald-100 px-6 py-2 text-sm font-bold leading-5 tracking-[-0.35px] text-emerald-800">
              {badge}
            </span>
          </div>
        </div>

        {/* Analysis Summary — Figma: right column ~65% (677.33 / 1040) */}
        <div className="flex min-w-0 flex-1 flex-col gap-6 lg:pl-8">
          <div className="flex flex-wrap items-center gap-3">
            <span className="font-display inline-flex items-center gap-2 rounded-2xl border border-sky-500/30 bg-sky-500/10 px-3 py-1 text-xs font-bold text-sky-600">
              <span className="inline-block h-3 w-3 rounded-sm bg-sky-500/80" aria-hidden />
              {data.ClearTag}
            </span>
            <span className="font-display inline-flex rounded-2xl border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-300 blur-[1px]">
              {data.Blurtag1}
            </span>
            <span className="font-display inline-flex rounded-2xl border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-300 blur-[2px]">
              {data.Blurtag2}
            </span>
          </div>

          <div className="relative isolate">
            <div className="flex flex-col gap-4">
              <h2 className="font-display text-xl font-bold leading-7 text-slate-900">
                Candidate Competitive Analysis
              </h2>
              <p className="font-display text-base font-medium leading-[26px] text-slate-600">
                Your profile demonstrates exceptional clinical foundation in operative dentistry and endodontics. Based
                on current admission trends for FTD‑DDS programs, your GPA and work experience place you&hellip;
              </p>
              <p className="font-display text-base font-medium leading-[26px] text-slate-600">
                Furthermore, the strategic analysis of your extracurricular activities suggests a high potential for
                leadership recognition within the ADEA framework, particularly when&hellip;
              </p>
            </div>
            <div
              className="pointer-events-none absolute bottom-0 left-0 right-0 z-[1] h-24 bg-gradient-to-t from-white to-transparent"
              aria-hidden
            />
          </div>
        </div>
      </div>
    </section>
  );
}
