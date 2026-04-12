import type { AnalysisResultPayload } from "@/lib/analysis.types";

type AnalysisTopStripProps = {
  data: AnalysisResultPayload;
};

export function AnalysisTopStrip({ data }: AnalysisTopStripProps) {
  const pills = [data.Country, data.degree, data.yearsOfExp];

  return (
    <section className="relative isolate w-full overflow-hidden bg-[rgba(201,230,255,0.3)] px-6 py-8 lg:px-[152px]">
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(70.71%_70.71%_at_50%_50%,#0EA5E9_2.95%,rgba(14,165,233,0)_2.95%)] opacity-[0.05]"
        aria-hidden
      />
      <div className="relative z-[1] mx-auto flex w-full max-w-[1136px] flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-sky-500">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden>
              <path
                d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                fill="#003751"
              />
            </svg>
          </div>
          <div className="flex min-w-0 flex-col gap-0.5">
            <h1 className="font-display text-2xl font-extrabold leading-8 tracking-[-0.6px] text-[#001E2F]">
              Your Analysis is Ready
            </h1>
            <p className="font-display text-sm font-medium leading-5 text-[#004C6E] opacity-80">
              Personalized Snapshot from your Questionnaire
            </p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {pills.map((label, index) => (
            <span
              key={`${label}-${index}`}
              className="font-display rounded-full border border-sky-500/20 bg-white px-4 py-1.5 text-xs font-bold uppercase tracking-[0.3px] text-sky-500"
            >
              {label}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
