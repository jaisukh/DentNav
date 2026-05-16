"use client";

import { useCallback, useEffect, useState } from "react";
import { AnalysisView } from "@/components/analysis/AnalysisView";
import { FullAnalysisView } from "@/components/analysis/FullAnalysisView";
import { InfoToast } from "@/components/ui/InfoToast";
import { fetchMyAnalysisFull, fetchMyAnalysisPreview } from "@/lib/api/analysis";
import {
  analysisHandoffStorageKey,
  clearAnalysisResultFromSession,
  peekAnalysisResultFromSession,
} from "@/lib/analysis-session";
import type { AnalysisFullPayload } from "@/lib/analysis-full.types";
import type { AnalysisPreviewPayload } from "@/lib/analysis.types";
import { useAuthStatus } from "@/lib/auth-status-context";

export default function LandingAnalysisPage() {
  const { hasPaid, ready } = useAuthStatus();

  // Full analysis state (paid users)
  const [fullData, setFullData] = useState<AnalysisFullPayload | null>(null);

  // Preview state (free users + handoff)
  const [previewData, setPreviewData] = useState<AnalysisPreviewPayload | null>(null);

  const [error, setError] = useState<string | null>(null);
  const [reclaimedToast, setReclaimedToast] = useState(false);
  const dismissReclaimed = useCallback(() => setReclaimedToast(false), []);

  // ── Paid path: fetch full analysis ──────────────────────────────────────────
  useEffect(() => {
    if (!ready || !hasPaid) return;
    let cancelled = false;

    fetchMyAnalysisFull()
      .then((payload) => {
        if (!cancelled) setFullData(payload as AnalysisFullPayload);
      })
      .catch(() => {
        if (!cancelled) setError("Unable to load your full analysis. Please try again.");
      });

    return () => { cancelled = true; };
  }, [ready, hasPaid]);

  // ── Unpaid path: existing handoff + server preview logic ─────────────────────
  useEffect(() => {
    if (!ready || hasPaid) return;
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
            setPreviewData(payload);
            sessionStorage.removeItem(analysisHandoffStorageKey(handoffId));
            clearAnalysisResultFromSession();
            if (window.location.search.includes("h=")) {
              window.history.replaceState(null, "", "/landing/analysis");
            }
          });
          return () => { cancelled = true; };
        } catch {
          /* fall through */
        }
      }
    }

    const fromQuestionnaire = peekAnalysisResultFromSession();
    if (fromQuestionnaire) {
      queueMicrotask(() => {
        if (!cancelled) {
          setPreviewData(fromQuestionnaire);
          clearAnalysisResultFromSession();
          if (window.location.search.includes("h=")) {
            window.history.replaceState(null, "", "/landing/analysis");
          }
        }
      });
      return () => { cancelled = true; };
    }

    if (fromServer || !handoffId) {
      if (reclaimed) queueMicrotask(() => { if (!cancelled) setReclaimedToast(true); });
      fetchMyAnalysisPreview()
        .then((payload) => {
          if (!cancelled) {
            setPreviewData(payload);
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
      return () => { cancelled = true; };
    }

    queueMicrotask(() => {
      if (!cancelled) setError("We couldn't load your results. Please return to the questionnaire and try again.");
    });
    return () => { cancelled = true; };
  }, [ready, hasPaid]);

  // ── Render ───────────────────────────────────────────────────────────────────

  if (error) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center font-display text-slate-600">
        {error}
      </div>
    );
  }

  if (!ready || (hasPaid ? !fullData : !previewData)) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center font-display text-slate-500">
        Loading analysis…
      </div>
    );
  }

  if (hasPaid && fullData) {
    return <FullAnalysisView data={fullData} />;
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
      <AnalysisView data={previewData!} insideLanding />
    </>
  );
}
