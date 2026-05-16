"use client";

import { useEffect } from "react";

type InfoToastProps = {
  open: boolean;
  onDismiss: () => void;
  title: string;
  body: string;
  /** ms before auto-dismiss; pass 0 to disable. */
  autoDismissMs?: number;
  /** "amber" for warnings (default), "sky" for informational. */
  tone?: "amber" | "sky";
};

const toneClasses = {
  amber:
    "border-amber-200/90 bg-amber-50/98 text-amber-950 [&_strong]:text-amber-900 [&_p]:text-amber-900/85 [&_button]:text-amber-800",
  sky:
    "border-sky-200/90 bg-sky-50/98 text-sky-950 [&_strong]:text-sky-900 [&_p]:text-sky-900/85 [&_button]:text-sky-800",
};

export function InfoToast({
  open,
  onDismiss,
  title,
  body,
  autoDismissMs = 10000,
  tone = "amber",
}: InfoToastProps) {
  useEffect(() => {
    if (!open || autoDismissMs <= 0) return;
    const t = setTimeout(onDismiss, autoDismissMs);
    return () => clearTimeout(t);
  }, [open, onDismiss, autoDismissMs]);

  if (!open) return null;

  return (
    <div
      className={`fixed left-1/2 top-20 z-100 max-w-md -translate-x-1/2 rounded-xl border px-4 py-3 text-sm shadow-[0_12px_40px_-12px_rgba(0,0,0,0.2)] ${toneClasses[tone]}`}
      role="status"
    >
      <p className="font-semibold">
        <strong>{title}</strong>
      </p>
      <p className="mt-1 leading-snug">{body}</p>
      <button
        type="button"
        onClick={onDismiss}
        className="mt-2 text-xs font-bold uppercase tracking-wide underline"
      >
        Dismiss
      </button>
    </div>
  );
}
