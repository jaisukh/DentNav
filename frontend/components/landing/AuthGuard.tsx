"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { BrandLogo } from "@/components/home/BrandLogo";
import { InfoToast } from "@/components/ui/InfoToast";
import { useAuthStatus } from "@/lib/auth-status-context";

const REDIRECT_DELAY_MS = 2500;

/**
 * Client-side session guard for the /landing layout.
 *
 * The middleware already blocks requests with no cookie at the Edge.
 * This component handles the next layer: a cookie exists but the backend
 * session is invalid or expired. It reads the shared auth status from the
 * `AuthStatusProvider` (root layout) so the underlying /access-status fetch
 * is shared with `<SignInLink>`, `<QuestionnaireLink>`, etc. — no duplicate
 * network calls per page load.
 */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const auth = useAuthStatus();
  const [staleToastDismissed, setStaleToastDismissed] = useState(false);
  const dismissDupToast = useCallback(() => setStaleToastDismissed(true), []);

  const showStaleToast =
    auth.staleQuestionnaireRemoved && !staleToastDismissed;

  // Derive from auth; avoid setState in an effect (eslint react-hooks/set-state-in-effect).
  const phase: "verifying" | "authenticated" | "failed" = !auth.ready
    ? "verifying"
    : auth.signedIn
      ? "authenticated"
      : "failed";

  useEffect(() => {
    if (phase !== "failed") return;
    const t = setTimeout(() => {
      router.replace("/auth/login?reason=session_expired");
    }, REDIRECT_DELAY_MS);
    return () => clearTimeout(t);
  }, [phase, router]);

  if (phase === "verifying") {
    return <VerifyingScreen />;
  }

  if (phase === "failed") {
    return <FailedScreen />;
  }

  return (
    <>
      <InfoToast
        open={showStaleToast}
        onDismiss={dismissDupToast}
        title="One questionnaire only"
        body="You already have a pathway analysis. A second submission was not kept; we only store your first questionnaire."
        tone="amber"
      />
      {children}
    </>
  );
}

// ─── Verifying screen ────────────────────────────────────────────────────────

function VerifyingScreen() {
  return (
    <div className="flex min-h-dvh flex-col items-center justify-center gap-8 bg-white px-4">
      <BrandLogo compact iconSize={32} />

      <div className="flex flex-col items-center gap-4">
        {/* Spinner */}
        <div
          className="h-9 w-9 animate-spin rounded-full border-[3px] border-[#E2E8F0] border-t-dent-sky"
          role="status"
          aria-label="Verifying your session"
        />

        <div className="text-center">
          <p className="text-sm font-semibold text-dent-ink">
            Authenticating
          </p>
          <p className="mt-1 text-xs text-[#64748B]">
            Verifying your session, just a moment…
          </p>
        </div>
      </div>
    </div>
  );
}

// ─── Failed screen ───────────────────────────────────────────────────────────

function FailedScreen() {
  return (
    <div className="flex min-h-dvh flex-col items-center justify-center gap-8 bg-white px-4">
      <BrandLogo compact iconSize={32} />

      <div className="flex flex-col items-center gap-4">
        {/* Error icon */}
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-50 ring-1 ring-red-100">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            className="h-5 w-5 text-red-500"
            aria-hidden
          >
            <path
              d="M18 6L6 18M6 6l12 12"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </div>

        <div className="text-center">
          <p className="text-sm font-semibold text-dent-ink">
            Authentication failed
          </p>
          <p className="mt-1 text-xs leading-relaxed text-[#64748B]">
            Your session has expired or could not be verified.
            <br />
            Redirecting you to sign in…
          </p>
        </div>

        {/* Redirect progress bar */}
        <div className="h-0.5 w-40 overflow-hidden rounded-full bg-[#F1F5F9]">
          <div
            className="h-full rounded-full bg-dent-sky"
            style={{
              animation: `grow ${REDIRECT_DELAY_MS}ms linear forwards`,
            }}
          />
        </div>
      </div>

      <style>{`
        @keyframes grow {
          from { width: 0% }
          to   { width: 100% }
        }
      `}</style>
    </div>
  );
}
