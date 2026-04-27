"use client";

import { useEffect, useState } from "react";
import { ModalShell } from "@/components/ui/ModalShell";
import {
  fetchMyAnalysisAnswers,
  type MyAnswersPayload,
} from "@/lib/api/analysis";
import type { AnswerValue, Question } from "@/lib/questionnaire.types";

type AnswersPreviewModalProps = {
  open: boolean;
  onClose: () => void;
};

function formatAnswer(value: AnswerValue | undefined): string | null {
  if (value === undefined) return null;
  if (Array.isArray(value)) {
    const cleaned = value.map((v) => v.trim()).filter(Boolean);
    return cleaned.length > 0 ? cleaned.join(", ") : null;
  }
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}

/**
 * Read-only modal that shows the user's previously submitted questionnaire
 * (Q -> A list). Blurs the rest of the page so the user can scan their
 * answers without losing the page they were on (e.g. /landing/packages).
 */
export function AnswersPreviewModal({
  open,
  onClose,
}: AnswersPreviewModalProps) {
  const [data, setData] = useState<MyAnswersPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    let active = true;
    // Clear stale Q&A in the same commit as `open` — deferring to a microtask
    // let one frame of old data flash on reopen. Async fetch is OK in `.then`
    // (eslint is fine with setState in promise callbacks, not the effect sync body).
    /* eslint-disable react-hooks/set-state-in-effect */
    setError(null);
    setData(null);
    setLoading(true);
    /* eslint-enable react-hooks/set-state-in-effect */
    void fetchMyAnalysisAnswers()
      .then((payload) => {
        if (active) setData(payload);
      })
      .catch(() => {
        if (active) setError("We couldn't load your previous response.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [open]);

  return (
    <ModalShell
      open={open}
      onClose={onClose}
      ariaLabel="Your previous response"
      widthClass="max-w-2xl"
      blurBackdrop
    >
      <div className="flex max-h-[82vh] flex-col">
        <div className="border-b border-[#E2E8F0] px-7 pb-4 pt-7">
          <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-dent-deep">
            Your previous response
          </p>
          <h2 className="mt-1.5 font-display text-xl font-bold text-dent-ink">
            Questionnaire on file
          </h2>
          <p className="mt-1.5 text-sm leading-relaxed text-[#64748B]">
            Read-only — this is the questionnaire we used to build your
            personalised analysis.
          </p>
        </div>

        <div className="flex-1 overflow-y-auto px-7 py-5">
          {loading ? (
            <p className="text-sm text-[#64748B]">Loading your response…</p>
          ) : error ? (
            <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-800">
              {error}
            </p>
          ) : data ? (
            <AnswersList
              questions={data.questionnaire.questions}
              answers={data.answers}
            />
          ) : null}
        </div>
      </div>
    </ModalShell>
  );
}

function AnswersList({
  questions,
  answers,
}: {
  questions: Question[];
  answers: Record<string, AnswerValue>;
}) {
  const ordered = [...questions].sort((a, b) => a.order - b.order);
  return (
    <ol className="space-y-5">
      {ordered.map((q, idx) => {
        const formatted = formatAnswer(answers[q.id]);
        return (
          <li
            key={q.id}
            className="rounded-xl border border-[#F1F5F9] bg-white px-4 py-3"
          >
            <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#94A3B8]">
              Question {idx + 1}
            </p>
            <p className="mt-1 text-sm font-semibold leading-snug text-dent-ink">
              {q.label}
            </p>
            {q.description ? (
              <p className="mt-1 text-xs leading-relaxed text-[#64748B]">
                {q.description}
              </p>
            ) : null}
            <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-[#3E4850]">
              {formatted ?? (
                <span className="italic text-[#94A3B8]">No answer</span>
              )}
            </p>
          </li>
        );
      })}
    </ol>
  );
}
