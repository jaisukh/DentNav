"use client";

import { useEffect, useState } from "react";
import { AnalysisView } from "@/components/analysis/AnalysisView";
import {
  analysisHandoffStorageKey,
  clearAnalysisResultFromSession,
  peekAnalysisResultFromSession,
} from "@/lib/analysis-session";
import { fetchAnalysis } from "@/lib/api/analysis";
import type { AnalysisResultPayload } from "@/lib/analysis.types";

export default function AnalysisPage() {
  const [data, setData] = useState<AnalysisResultPayload | null>(() => {
    if (typeof window === "undefined") return null;
    const params = new URLSearchParams(window.location.search);
    const handoffId = params.get("h");
    if (handoffId) {
      const raw = sessionStorage.getItem(analysisHandoffStorageKey(handoffId));
      if (raw) {
        try {
          return JSON.parse(raw) as AnalysisResultPayload;
        } catch {
          /* fall through to legacy / GET */
        }
      }
    }
    return peekAnalysisResultFromSession();
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const params = new URLSearchParams(window.location.search);
    const handoffId = params.get("h");
    if (data) {
      queueMicrotask(() => {
        if (!cancelled) {
          if (handoffId) {
            sessionStorage.removeItem(analysisHandoffStorageKey(handoffId));
          }
          clearAnalysisResultFromSession();
          if (window.location.pathname === "/analysis" && window.location.search.includes("h=")) {
            window.history.replaceState(null, "", "/analysis");
          }
        }
      });
      return () => {
        cancelled = true;
      };
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
  }, [data]);

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
