"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";

type ModalShellProps = {
  open: boolean;
  onClose: () => void;
  /** Provide an aria label for screen readers. */
  ariaLabel: string;
  /** Tailwind size override for the inner card. Defaults to `max-w-md`. */
  widthClass?: string;
  /** When true, the backdrop blurs the page; otherwise it's just dimmed. */
  blurBackdrop?: boolean;
  children: ReactNode;
};

/**
 * Centered, accessible modal with a fixed backdrop. Closes on Escape and on
 * backdrop click. Includes a top-right X button and (when blurBackdrop is
 * true) a heavier backdrop blur — used for the "Review your response" modal.
 *
 * Rendered through a portal into `document.body` so that ancestors using
 * `transform`, `filter`, or `backdrop-filter` (e.g. the sticky NavBar with
 * `backdrop-blur-md`) cannot trap `position: fixed` and slam the modal to
 * the top of the page.
 */
export function ModalShell({
  open,
  onClose,
  ariaLabel,
  widthClass = "max-w-md",
  blurBackdrop = false,
  children,
}: ModalShellProps) {
  const cardRef = useRef<HTMLDivElement | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Defer past the effect's synchronous run — the portal must only
    // render on the client where `document.body` exists; the linter
    // rejects a synchronous setState in the effect body.
    const id = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(id);
  }, []);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [open, onClose]);

  if (!open || !mounted) return null;

  const overlay = (
    <div
      className={`fixed inset-0 z-[100] flex items-center justify-center px-4 py-6 ${
        blurBackdrop
          ? "bg-slate-900/40 backdrop-blur-md"
          : "bg-slate-900/50 backdrop-blur-[2px]"
      }`}
      role="dialog"
      aria-modal="true"
      aria-label={ariaLabel}
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        ref={cardRef}
        className={`relative w-full ${widthClass} rounded-2xl border border-[#E2E8F0] bg-white shadow-[0_30px_80px_-24px_rgba(13,28,46,0.45)]`}
      >
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="absolute right-3 top-3 z-10 inline-flex h-9 w-9 items-center justify-center rounded-full border border-[#E2E8F0] bg-white text-[#475569] shadow-sm transition-colors hover:border-dent-sky/40 hover:bg-slate-50 hover:text-dent-ink focus:outline-none focus:ring-2 focus:ring-dent-sky/40"
        >
          <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden>
            <path
              d="M18 6L6 18M6 6l12 12"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </button>
        {children}
      </div>
    </div>
  );

  return createPortal(overlay, document.body);
}
