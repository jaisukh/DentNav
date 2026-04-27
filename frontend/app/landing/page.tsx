"use client";

import { useCallback, useEffect, useState } from "react";
import { BrochureDownload } from "@/components/landing/BrochureDownload";
import { LandingVideoSection } from "@/components/landing/LandingVideoSection";
import { PaymentPrompt } from "@/components/landing/PaymentPrompt";
import { QuestionnairePrompt } from "@/components/landing/QuestionnairePrompt";
import { ViewAnalysis } from "@/components/landing/ViewAnalysis";
import { InfoToast } from "@/components/ui/InfoToast";
import { useAuthStatus } from "@/lib/auth-status-context";

export default function LandingPage() {
  // Reads the single /access-status fetch initiated by AuthStatusProvider in
  // app/layout.tsx — every other landing component (AuthGuard, NavBar links,
  // packages CTA, etc.) shares this same value, so the endpoint is hit once
  // per page load instead of 3–5 times.
  const status = useAuthStatus();
  const [reclaimedToast, setReclaimedToast] = useState(false);
  const dismissReclaimed = useCallback(() => setReclaimedToast(false), []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    if (params.get("reclaimed_existing") === "1") {
      setReclaimedToast(true);
      params.delete("reclaimed_existing");
      const next = params.toString();
      window.history.replaceState(
        null,
        "",
        `${window.location.pathname}${next ? `?${next}` : ""}`,
      );
    }
  }, []);

  return (
    <div className="w-full max-w-6xl pb-6">
      <InfoToast
        open={reclaimedToast}
        onDismiss={dismissReclaimed}
        title="You're viewing your previous response"
        body="We kept the analysis already on your account and dropped the new submission. Only one questionnaire is stored per user."
        tone="sky"
      />


      {/* ── Hero ─────────────────────────────────────────────────────── */}
      <header className="mb-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between lg:gap-8">
          <div className="min-w-0 max-w-3xl flex-1">

            {/* Live status pill */}
            <div className="inline-flex items-center gap-2 rounded-full border border-dent-sky/25 bg-white/90 px-3 py-1 shadow-[0_6px_18px_-10px_rgba(14,165,233,0.45)]">
            <span className="relative flex h-2 w-2" aria-hidden>
  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-dent-sky opacity-75" />
  <span className="relative inline-flex h-2 w-2 rounded-full bg-dent-sky" />
</span>
              <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-dent-deep">
                Your licensing dashboard
              </span>
            </div>

            <h1 className="mt-4 font-display text-3xl font-bold tracking-tight text-dent-ink sm:text-[2.5rem] sm:leading-[1.08]">
              Welcome —{" "}
              <span className="bg-gradient-to-r from-dent-deep via-dent-sky to-[#38BDF8] bg-clip-text text-transparent">
                your U.S. licensing roadmap
              </span>{" "}
              is ready to personalize.
            </h1>

            <p className="mt-4 max-w-3xl text-sm leading-relaxed text-[#475569] sm:text-base">
              One place for every exam, credential requirement, and state-specific licensing rule — filtered to your profile, target states, and program type.
            </p>

            <div className="mt-4 grid gap-2 sm:grid-cols-3">
              {[
                { label: "Tailored",  body: "Guidance built on your answers" },
                { label: "Focused",   body: "Exams, docs, and sequencing" },
                { label: "One place", body: "Pick up anytime, on any device" },
              ].map(({ label, body }) => (
                <div key={label} className="rounded-xl border border-[#E2E8F0] bg-white/80 px-3 py-2.5 shadow-sm">
                  <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#94A3B8]">{label}</p>
                  <p className="mt-0.5 text-xs font-semibold leading-snug text-dent-ink">{body}</p>
                </div>
              ))}
            </div>
          </div>
          <BrochureDownload />
        </div>
      </header>

      {/* ── Prompt card ──────────────────────────────────────────────── */}
      <div className="w-full">
        {!status.ready ? (
          <div className="rounded-3xl border border-[#E2E8F0] bg-white p-8 text-sm font-medium text-[#64748B]">
            Checking your account progress...
          </div>
        ) : !status.hasAnsweredQuestionnaire ? (
          <QuestionnairePrompt />
        ) : !status.hasPaid ? (
          <PaymentPrompt />
        ) : (
          <ViewAnalysis />
        )}
      </div>

      <LandingVideoSection />
    </div>
  );
}
