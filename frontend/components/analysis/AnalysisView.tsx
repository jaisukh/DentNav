import type { AnalysisPreviewPayload } from "@/lib/analysis.types";
import { Footer } from "@/components/home/Footer";
import { NavBar } from "@/components/home/NavBar";
import { AnalysisTopStrip } from "./AnalysisTopStrip";
import { BlurredRoadmapSection } from "./BlurredRoadmapSection";
import { ReadinessScoreCard } from "./ReadinessScoreCard";

type AnalysisViewProps = {
  data: AnalysisPreviewPayload;
};

export function AnalysisView({ data }: AnalysisViewProps) {
  return (
    <div className="relative isolate flex min-h-dvh w-full flex-col bg-white font-display text-dent-ink">
      <NavBar />

      <main className="relative flex w-full flex-col items-stretch">
        <div className="relative bg-[rgba(201,230,255,0.3)] pb-8">
          <AnalysisTopStrip data={data} />
          <div className="relative mt-3 px-6 lg:px-[152px]">
            <ReadinessScoreCard data={data.readinessScore} />
          </div>
        </div>

        <div className="relative">
          <BlurredRoadmapSection />
        </div>
      </main>

      <Footer />
    </div>
  );
}
