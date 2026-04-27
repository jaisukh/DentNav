"use client";

import {
  type ReactNode,
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";
import {
  type LandingAccessStatus,
  applyStaleRemovalSync,
  fetchLandingAccessStatus,
  toLandingStatus,
} from "@/lib/api/landing";

export type AuthStatus = LandingAccessStatus & {
  loading: boolean;
  /** True once the request resolved (regardless of success). */
  ready: boolean;
  /** True only when the server header signaled the duplicate-row cleanup. */
  staleQuestionnaireRemoved: boolean;
};

const DEFAULT: AuthStatus = {
  signedIn: false,
  hasAnsweredQuestionnaire: false,
  hasPaid: false,
  latestAnalysisId: null,
  loading: true,
  ready: false,
  staleQuestionnaireRemoved: false,
};

const AuthStatusContext = createContext<AuthStatus | null>(null);

/**
 * Provider that performs a single `/access-status` fetch on mount and shares
 * the result with every descendant via React context.
 *
 * Wrap once near the root of the app (in `app/layout.tsx`) so that all of
 * `<SignInLink>`, `<QuestionnaireLink>`, `<OneTimeAccessCTA>`, the navbar
 * components, and the AuthGuard share the same network request instead of
 * each issuing their own. Without this, a typical /landing page load would
 * hit `/access-status` 3–5 times concurrently.
 */
export function AuthStatusProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthStatus>(DEFAULT);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const result = await fetchLandingAccessStatus();
        if (!active) return;
        applyStaleRemovalSync(result);
        const status = toLandingStatus(result);
        setState({
          ...status,
          loading: false,
          ready: true,
          staleQuestionnaireRemoved: result.staleQuestionnaireRemoved,
        });
      } catch {
        if (!active) return;
        setState({
          ...DEFAULT,
          loading: false,
          ready: true,
        });
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  return (
    <AuthStatusContext.Provider value={state}>
      {children}
    </AuthStatusContext.Provider>
  );
}

/**
 * Read the current auth status. Must be used inside `<AuthStatusProvider>`.
 * If no provider is mounted (e.g. an isolated test, or an island that escapes
 * the root layout) we degrade gracefully to the DEFAULT value rather than
 * throwing — this keeps marketing-only pages safe.
 */
export function useAuthStatus(): AuthStatus {
  const ctx = useContext(AuthStatusContext);
  return ctx ?? DEFAULT;
}
