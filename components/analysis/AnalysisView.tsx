import type { AnalysisResultPayload } from "@/lib/analysis.types";
import { AnalysisFooter } from "./AnalysisFooter";
import { AnalysisResultsCard } from "./AnalysisResultsCard";
import { AnalysisTopNav } from "./AnalysisTopNav";
import { AnalysisTopStrip } from "./AnalysisTopStrip";
import { BlurredRoadmapSection } from "./BlurredRoadmapSection";

type AnalysisViewProps = {
  data: AnalysisResultPayload;
};

export function AnalysisView({ data }: AnalysisViewProps) {
  return (
    <div className="relative isolate flex min-h-dvh w-full flex-col bg-white font-display">
      <AnalysisTopNav />

      <main className="relative flex w-full flex-1 flex-col items-stretch">
        {/* Overlap: strip sits under nav; card overlaps strip (Figma: card top ~206px from frame, strip starts ~96px) */}
        <div className="relative pt-0">
          <AnalysisTopStrip data={data} />
          <div className="relative z-[2] -mt-14 px-6 sm:-mt-16 lg:px-[152px]">
            <AnalysisResultsCard data={data} />
          </div>
        </div>

        <div className="relative flex-1">
          <BlurredRoadmapSection />
        </div>
      </main>

      <AnalysisFooter />
    </div>
  );
}
