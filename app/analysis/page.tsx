import { AnalysisView } from "@/components/analysis/AnalysisView";
import analysisMock from "@/data/analysis-mock.json";
import type { AnalysisResultPayload } from "@/lib/analysis.types";

export default function AnalysisPage() {
  const data = analysisMock as AnalysisResultPayload;
  return <AnalysisView data={data} />;
}
