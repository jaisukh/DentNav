"use client";

import { useEffect, useState } from "react";
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

/**
 * Single source of truth for the navbar/page-level access flags.
 *
 * Re-uses the existing /access-status endpoint so callers benefit from the
 * stale-questionnaire cleanup (X-Removed-Stale-Questionnaire header) without
 * needing to wire it themselves.
 */
export function useAuthStatus(): AuthStatus {
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

  return state;
}
