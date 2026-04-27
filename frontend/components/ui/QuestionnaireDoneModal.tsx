"use client";

import Link from "next/link";
import { ModalShell } from "@/components/ui/ModalShell";

type QuestionnaireDoneModalProps = {
  open: boolean;
  onClose: () => void;
};

/**
 * Shown when a signed-in user with an existing analysis tries to start the
 * questionnaire again. Closing the modal does NOT navigate to the form.
 */
export function QuestionnaireDoneModal({
  open,
  onClose,
}: QuestionnaireDoneModalProps) {
  return (
    <ModalShell
      open={open}
      onClose={onClose}
      ariaLabel="You already have an analysis"
    >
      <div className="px-7 pb-7 pt-9 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-sky-50 ring-1 ring-sky-100">
          <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5 text-dent-deep" aria-hidden>
            <path
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              stroke="currentColor"
              strokeWidth="1.75"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M9 13l2 2 4-4"
              stroke="currentColor"
              strokeWidth="1.75"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        <h2 className="mt-4 font-display text-lg font-bold text-dent-ink">
          You already have a generated analysis
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-[#475569]">
          We only keep a single questionnaire on file. You can preview your
          existing analysis or jump straight to your dashboard.
        </p>
        <div className="mt-6 flex flex-col gap-2.5">
          <Link
            href="/analysis?source=server"
            onClick={onClose}
            className="inline-flex w-full items-center justify-center rounded-full bg-dent-sky px-5 py-2.5 text-sm font-bold text-white transition-opacity hover:opacity-90 active:scale-[0.98]"
          >
            Preview your analysis
          </Link>
          <Link
            href="/landing"
            onClick={onClose}
            className="inline-flex w-full items-center justify-center rounded-full border border-[#E2E8F0] bg-white px-5 py-2.5 text-sm font-bold text-dent-ink transition-colors hover:border-dent-sky/40 hover:bg-dent-badge-bg/50 active:scale-[0.98]"
          >
            Go to landing page
          </Link>
        </div>
      </div>
    </ModalShell>
  );
}
