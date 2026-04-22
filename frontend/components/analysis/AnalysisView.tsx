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
    <div className="relative isolate flex min-h-dvh w-full flex-col bg-[#F8F9FF] font-display text-dent-ink">
      <NavBar />

      <main className="relative flex w-full flex-col items-stretch">
        {/* Soft strip + compact “ready” panel; extra bottom padding reserves space for overlap */}
        <div className="relative bg-[rgba(201,230,255,0.3)] px-4 pb-20 pt-8 sm:px-6 lg:px-[152px] lg:pb-24">
          <div className="relative z-[1] mx-auto w-full max-w-[1136px]">
            <AnalysisTopStrip data={data} />
          </div>
        </div>

        {/* White band ties readiness card to “Unlock your full roadmap” (same surface) */}
        <div className="relative z-[2] bg-white">
          <div className="-mt-14 px-4 pt-0 sm:px-6 lg:px-[152px] lg:-mt-16">
            <div className="mx-auto w-full max-w-[1136px]">
              <ReadinessScoreCard data={data.readinessScore} />
            </div>
          </div>
          <BlurredRoadmapSection />
        </div>
      </main>

      <Footer />
    </div>
  );
}
