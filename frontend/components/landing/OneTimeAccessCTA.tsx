"use client";

import { useState } from "react";
import Link from "next/link";
import { QuestionnaireLink } from "@/components/questionnaire/QuestionnaireLink";
import { AnalysisAccessModal } from "@/components/landing/AnalysisAccessModal";
import { AnswersPreviewModal } from "@/components/ui/AnswersPreviewModal";
import { useAuthStatus } from "@/lib/auth-status-context";

function Arrow({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg viewBox="0 0 16 16" fill="none" className={className} aria-hidden>
      <path
        d="M3.33 8h9.34M8.67 4l4 4-4 4"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

const PRIMARY_BTN =
  "dentnav-cta-primary group relative flex w-full items-center justify-center gap-2.5 rounded-xl bg-dent-sky py-3.5 text-sm font-bold text-white";

const SECONDARY_BTN =
  "flex w-full items-center justify-center rounded-xl border border-white/15 py-3 text-sm font-semibold text-white/70 transition-colors hover:border-white/30 hover:text-white";

export function OneTimeAccessCTA() {
  const auth = useAuthStatus();
  const [accessModalOpen, setAccessModalOpen] = useState(false);
  const [answersOpen, setAnswersOpen] = useState(false);

  const helperCopy = !auth.ready
    ? "Checking your access…"
    : auth.hasPaid
      ? "Analysis unlocked — open it any time from your dashboard."
      : auth.hasAnsweredQuestionnaire
        ? "Single purchase — permanent access to your personalised roadmap."
        : "Complete the questionnaire to generate your analysis.";

  const headlineCopy = !auth.ready
    ? "Your analysis is ready"
    : auth.hasPaid
      ? "Analysis unlocked"
      : auth.hasAnsweredQuestionnaire
        ? "Your analysis is ready"
        : "Start with the questionnaire";

  const buttons = renderButtons({
    ready: auth.ready,
    hasAnsweredQuestionnaire: auth.hasAnsweredQuestionnaire,
    hasPaid: auth.hasPaid,
    onGetAccess: () => setAccessModalOpen(true),
    onViewResponse: () => setAnswersOpen(true),
  });

  return (
    <>
      <div className="flex flex-col items-center justify-center text-center lg:pl-12">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 text-[#7DD3FC] ring-1 ring-white/15">
          <IconAnalysis />
        </div>

        <p className="mt-5 font-display text-lg font-bold text-white">
          {headlineCopy}
        </p>
        <p className="mt-2 text-sm leading-relaxed text-white/60">
          {helperCopy}
        </p>

        <div className="mt-8 flex w-full flex-col gap-3">{buttons}</div>
      </div>

      {accessModalOpen && <AnalysisAccessModal onClose={() => setAccessModalOpen(false)} />}
      <AnswersPreviewModal open={answersOpen} onClose={() => setAnswersOpen(false)} />
    </>
  );
}

function renderButtons(flags: {
  ready: boolean;
  hasAnsweredQuestionnaire: boolean;
  hasPaid: boolean;
  onGetAccess: () => void;
  onViewResponse: () => void;
}) {
  if (!flags.ready) {
    return (
      <QuestionnaireLink href="/landing/questionnaire" className={PRIMARY_BTN}>
        <span className="dentnav-cta-primary__halo" aria-hidden />
        <span className="dentnav-cta-primary__shine" aria-hidden />
        <span className="relative z-10 flex items-center gap-2.5">
          Get started
          <Arrow className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
        </span>
      </QuestionnaireLink>
    );
  }

  if (!flags.hasAnsweredQuestionnaire) {
    return (
      <QuestionnaireLink href="/landing/questionnaire" className={PRIMARY_BTN}>
        <span className="dentnav-cta-primary__halo" aria-hidden />
        <span className="dentnav-cta-primary__shine" aria-hidden />
        <span className="relative z-10 flex items-center gap-2.5">
          Go to questionnaire
          <Arrow className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
        </span>
      </QuestionnaireLink>
    );
  }

  if (flags.hasPaid) {
    return (
      <>
        <Link href="/landing/analysis?source=server" className={PRIMARY_BTN}>
          <span className="dentnav-cta-primary__halo" aria-hidden />
          <span className="dentnav-cta-primary__shine" aria-hidden />
          <span className="relative z-10 flex items-center gap-2.5">
            View analysis
            <Arrow className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </span>
        </Link>
        <button type="button" onClick={flags.onViewResponse} className={SECONDARY_BTN}>
          View your response
        </button>
      </>
    );
  }

  return (
    <>
      <button type="button" onClick={flags.onGetAccess} className={PRIMARY_BTN}>
        <span className="dentnav-cta-primary__halo" aria-hidden />
        <span className="dentnav-cta-primary__shine" aria-hidden />
        <span className="relative z-10 flex items-center gap-2.5">
          Get access
          <Arrow className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
        </span>
      </button>
      <button type="button" onClick={flags.onViewResponse} className={SECONDARY_BTN}>
        View your response
      </button>
    </>
  );
}

function IconAnalysis() {
  return (
    <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6" aria-hidden>
      <path
        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
