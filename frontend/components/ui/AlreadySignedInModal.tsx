"use client";

import Link from "next/link";
import { ModalShell } from "@/components/ui/ModalShell";

type AlreadySignedInModalProps = {
  open: boolean;
  onClose: () => void;
};

/** Used wherever a "Sign In" entry point is hit while the user already has a session. */
export function AlreadySignedInModal({ open, onClose }: AlreadySignedInModalProps) {
  return (
    <ModalShell
      open={open}
      onClose={onClose}
      ariaLabel="You're already signed in"
    >
      <div className="px-7 pb-7 pt-9 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50 ring-1 ring-emerald-100">
          <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5 text-emerald-600" aria-hidden>
            <path
              d="M5 12.5l4.5 4.5L19 7"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        <h2 className="mt-4 font-display text-lg font-bold text-dent-ink">
          You&apos;re already signed in
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-[#475569]">
          Your DentNav session is active. Head to your landing page to pick up
          where you left off.
        </p>
        <Link
          href="/landing"
          onClick={onClose}
          className="mt-6 inline-flex w-full items-center justify-center rounded-full bg-dent-sky px-5 py-2.5 text-sm font-bold text-white transition-opacity hover:opacity-90 active:scale-[0.98]"
        >
          Go to landing page
        </Link>
      </div>
    </ModalShell>
  );
}
