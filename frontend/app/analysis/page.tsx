"use client";

import { useEffect, useState } from "react";
import { AnalysisView } from "@/components/analysis/AnalysisView";
import { fetchMyAnalysisPreview } from "@/lib/api/analysis";
import {
  analysisHandoffStorageKey,
  clearAnalysisResultFromSession,
  peekAnalysisResultFromSession,
} from "@/lib/analysis-session";
import type { AnalysisPreviewPayload } from "@/lib/analysis.types";

export default function AnalysisPage() {
  const [data, setData] = useState<AnalysisPreviewPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const params = new URLSearchParams(window.location.search);
    const handoffId = params.get("h");
    const fromServer = params.get("source") === "server";

    if (handoffId) {
      const raw = sessionStorage.getItem(analysisHandoffStorageKey(handoffId));
      if (raw) {
        try {
          const payload = JSON.parse(raw) as AnalysisPreviewPayload;
          queueMicrotask(() => {
            if (cancelled) return;
            setData(payload);
            sessionStorage.removeItem(analysisHandoffStorageKey(handoffId));
            clearAnalysisResultFromSession();
            if (window.location.pathname === "/analysis" && window.location.search.includes("h=")) {
              window.history.replaceState(null, "", "/analysis");
            }
          });
          return () => {
            cancelled = true;
          };
        } catch {
          /* fall through to legacy session */
        }
      }
    }

    const fromQuestionnaire = peekAnalysisResultFromSession();
    if (fromQuestionnaire) {
      queueMicrotask(() => {
        if (!cancelled) {
          setData(fromQuestionnaire);
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

    // No client-side handoff. Fall back to the server preview when the user
    // is signed in and has a stored analysis. This is what the
    // QuestionnaireDoneModal -> "Preview your analysis" entrypoint relies on.
    if (fromServer || !handoffId) {
      fetchMyAnalysisPreview()
        .then((payload) => {
          if (!cancelled) {
            setData(payload);
            if (
              window.location.pathname === "/analysis" &&
              window.location.search.length > 0
            ) {
              window.history.replaceState(null, "", "/analysis");
            }
          }
        })
        .catch(() => {
          if (!cancelled) {
            setError(
              "No analysis on file. Please complete the questionnaire to generate one.",
            );
          }
        });
      return () => {
        cancelled = true;
      };
    }

    queueMicrotask(() => {
      if (!cancelled) {
        setError(
          "We couldn't load your results. Please return to the questionnaire and try again.",
        );
      }
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
