import { normalizeBodyParagraphs, truncateIntro } from "@/lib/analysis-body";
import { readinessLabel } from "@/lib/analysis-readiness";
import type { AnalysisResultPayload } from "@/lib/analysis.types";
import { AnalysisInsightStrip } from "./AnalysisInsightStrip";
import { ScoreGauge } from "./ScoreGauge";

type AnalysisResultsCardProps = {
  data: AnalysisResultPayload;
};

const INTRO_TEASER_MAX_CHARS = 200;
/** Max characters shown from paragraph 2 onward (before gradient); remainder is implied by "…". */
const FOLLOWING_TEASER_MAX_CHARS = 220;

export function AnalysisResultsCard({ data }: AnalysisResultsCardProps) {
  const badge = readinessLabel(data.Performance);
  const paragraphs = normalizeBodyParagraphs(data.Body);
  const introFull = paragraphs[0] ?? "";
  const followingParagraphs = paragraphs.slice(1);
  const followingFull = followingParagraphs.join("\n\n").trim();
  const hasFollowing = followingFull.length > 0;
  const introVisible = hasFollowing ? truncateIntro(introFull, INTRO_TEASER_MAX_CHARS) : introFull;
  const followingVisible = hasFollowing ? truncateIntro(followingFull, FOLLOWING_TEASER_MAX_CHARS) : "";
  const followingTruncated = hasFollowing && followingVisible.length < followingFull.length;

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
          <AnalysisInsightStrip />

          <div className="relative isolate">
            <div className="flex flex-col gap-4">
              <h2 className="font-display text-xl font-bold leading-7 text-slate-900">
                Candidate Competitive Analysis
              </h2>
              {introVisible ? (
                <p className="font-display text-base font-medium leading-[26px] text-slate-600">
                  {introVisible}
                  {hasFollowing ? "…" : ""}
                </p>
              ) : null}
              {hasFollowing ? (
                <p className="font-display whitespace-pre-line text-base font-medium leading-[26px] text-slate-600">
                  {followingVisible}
                  {followingTruncated ? "…" : ""}
                </p>
              ) : null}
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
