"use client";

import { useEffect, useState } from "react";
import { AnalysisView } from "@/components/analysis/AnalysisView";
import { takeAnalysisResultFromSession } from "@/lib/analysis-session";
import { fetchAnalysis } from "@/lib/api/analysis";
import type { AnalysisResultPayload } from "@/lib/analysis.types";

export default function AnalysisPage() {
  const [data, setData] = useState<AnalysisResultPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const fromQuestionnaire = takeAnalysisResultFromSession();
    if (fromQuestionnaire) {
      setData(fromQuestionnaire);
      return;
    }
    fetchAnalysis()
      .then((payload) => {
        if (!cancelled) setData(payload);
      })
      .catch(() => {
        if (!cancelled) setError("Could not load analysis.");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <div className="flex min-h-dvh items-center justify-center bg-white font-display text-slate-600">
        {error}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex min-h-dvh items-center justify-center bg-white font-display text-slate-500">
        Loading analysis…
      </div>
    );
  }

  return <AnalysisView data={data} />;
}
