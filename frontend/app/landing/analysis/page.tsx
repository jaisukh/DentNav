"use client";

import { useCallback, useEffect, useState } from "react";
import { AnalysisView } from "@/components/analysis/AnalysisView";
import { InfoToast } from "@/components/ui/InfoToast";
import { fetchMyAnalysisPreview } from "@/lib/api/analysis";
import {
  analysisHandoffStorageKey,
  clearAnalysisResultFromSession,
  peekAnalysisResultFromSession,
} from "@/lib/analysis-session";
import type { AnalysisPreviewPayload } from "@/lib/analysis.types";

export default function LandingAnalysisPage() {
  const [data, setData] = useState<AnalysisPreviewPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reclaimedToast, setReclaimedToast] = useState(false);
  const dismissReclaimed = useCallback(() => setReclaimedToast(false), []);

  useEffect(() => {
    let cancelled = false;

    const params = new URLSearchParams(window.location.search);
    const handoffId = params.get("h");
    const fromServer = params.get("source") === "server";
    const reclaimed = params.get("reclaimed_existing") === "1";

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
            if (window.location.search.includes("h=")) {
              window.history.replaceState(null, "", "/landing/analysis");
            }
          });
          return () => {
            cancelled = true;
          };
        } catch {
          /* fall through to session storage */
        }
      }
    }

    const fromQuestionnaire = peekAnalysisResultFromSession();
    if (fromQuestionnaire) {
      queueMicrotask(() => {
        if (!cancelled) {
          setData(fromQuestionnaire);
          clearAnalysisResultFromSession();
          if (window.location.search.includes("h=")) {
            window.history.replaceState(null, "", "/landing/analysis");
          }
        }
      });
      return () => {
        cancelled = true;
      };
    }

    if (fromServer || !handoffId) {
      if (reclaimed) queueMicrotask(() => { if (!cancelled) setReclaimedToast(true); });
      fetchMyAnalysisPreview()
        .then((payload) => {
          if (!cancelled) {
            setData(payload);
            if (window.location.search.length > 0) {
              window.history.replaceState(null, "", "/landing/analysis");
            }
          }
        })
        .catch(() => {
          if (!cancelled) {
            setError("No analysis on file. Please complete the questionnaire to generate one.");
          }
        });
      return () => {
        cancelled = true;
      };
    }

    queueMicrotask(() => {
      if (!cancelled) {
        setError("We couldn't load your results. Please return to the questionnaire and try again.");
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center font-display text-slate-600">
        {error}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center font-display text-slate-500">
        Loading analysis…
      </div>
    );
  }

  return (
    <>
      <InfoToast
        open={reclaimedToast}
        onDismiss={dismissReclaimed}
        title="You already have an analysis on file"
        body="We're showing your previous results. Only one analysis is stored per account."
        tone="sky"
      />
      <AnalysisView data={data} insideLanding />
    </>
  );
}
