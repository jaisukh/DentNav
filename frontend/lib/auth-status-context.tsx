"use client";

import {
  type ReactNode,
  createContext,
  useCallback,
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

export type AuthStatusContextValue = AuthStatus & {
  /**
   * Re-fetch /access-status from the backend and update every consumer.
   * Call this any time we know the cookie state may have changed
   * (sign-out, the analysis-claim redirect after OAuth callback, etc.).
   */
  refresh: () => Promise<void>;
  /**
   * Optimistic local clear — flip every consumer to "signed out" without
   * waiting for a network round-trip. The backend is still the source of
   * truth on the next refresh, but this avoids the brief window where the
   * cookie is gone but stale `signedIn: true` is still in memory after a
   * client-side sign-out.
   */
  clear: () => void;
};

const DEFAULT_AUTH: AuthStatus = {
  signedIn: false,
  hasAnsweredQuestionnaire: false,
  hasPaid: false,
  latestAnalysisId: null,
  loading: true,
  ready: false,
  staleQuestionnaireRemoved: false,
};

const DEFAULT_VALUE: AuthStatusContextValue = {
  ...DEFAULT_AUTH,
  refresh: async () => {},
  clear: () => {},
};

const AuthStatusContext = createContext<AuthStatusContextValue | null>(null);

/**
 * Provider that performs a single `/access-status` fetch on mount and shares
 * the result with every descendant via React context.
 *
 * Wrap once near the root of the app (in `app/layout.tsx`) so that all of
 * `<SignInLink>`, `<QuestionnaireLink>`, `<OneTimeAccessCTA>`, the navbar
 * components, and the AuthGuard share the same network request instead of
 * each issuing their own.
 *
 * The provider lives in the root layout, which means it survives
 * client-side navigation. Components that mutate the auth state
 * (sign-out, OAuth callback redirect) must call `refresh()` on the
 * returned context — otherwise the cached `signedIn: true` from a
 * previous session would persist in memory after the cookie is cleared.
 */
export function AuthStatusProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthStatus>(DEFAULT_AUTH);

  const refresh = useCallback(async () => {
    try {
      const result = await fetchLandingAccessStatus();
      applyStaleRemovalSync(result);
      const status = toLandingStatus(result);
      setState({
        ...status,
        loading: false,
        ready: true,
        staleQuestionnaireRemoved: result.staleQuestionnaireRemoved,
      });
    } catch {
      setState({
        ...DEFAULT_AUTH,
        loading: false,
        ready: true,
      });
    }
  }, []);

  const clear = useCallback(() => {
    setState({
      ...DEFAULT_AUTH,
      loading: false,
      ready: true,
    });
  }, []);

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
          ...DEFAULT_AUTH,
          loading: false,
          ready: true,
        });
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  const value: AuthStatusContextValue = { ...state, refresh, clear };

  return (
    <AuthStatusContext.Provider value={value}>
      {children}
    </AuthStatusContext.Provider>
  );
}

/**
 * Read the current auth status (and refresh/clear actions). Must be used
 * inside `<AuthStatusProvider>`. If no provider is mounted (e.g. an
 * isolated test, or an island that escapes the root layout) we degrade
 * gracefully to the DEFAULT value rather than throwing — this keeps
 * marketing-only pages safe.
 */
export function useAuthStatus(): AuthStatusContextValue {
  const ctx = useContext(AuthStatusContext);
  return ctx ?? DEFAULT_VALUE;
}
