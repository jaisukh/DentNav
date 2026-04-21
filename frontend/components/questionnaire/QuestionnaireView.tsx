"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import { NavBar } from "@/components/home/NavBar";
import { analysisHandoffStorageKey, storeAnalysisResult } from "@/lib/analysis-session";
import { fetchQuestionnaire } from "@/lib/api/questionnaire";
import { submitAnalysis } from "@/lib/api/analysis";
import type { AnswerValue, Question, QuestionnaireDocument } from "@/lib/questionnaire.types";
import { QuestionnaireField } from "./QuestionnaireField";

/** Shown above the form; not part of S3 payload. */
const QUESTIONNAIRE_HEADING_TITLE = "Tell Us About Yourself";
const QUESTIONNAIRE_HEADING_SUBTITLE = "Get a Personalized Roadmap matching your Profile";

function isAnswerComplete(
  q: Question,
  val: AnswerValue | undefined,
  allAnswers: Record<string, AnswerValue>,
): boolean {
  if (q.type === "dropdown" && q.dependsOn) {
    const parent = allAnswers[q.dependsOn.questionId];
    if (typeof parent !== "string" || !parent.trim()) return false;
  }
  if (val === undefined) return false;
  if (q.type === "multiSelect") {
    if (!Array.isArray(val)) return false;
    const min = q.minSelections ?? 1;
    const max = q.maxSelections ?? Infinity;
    return val.length >= min && val.length <= max;
  }
  if (typeof val === "string") return val.trim().length > 0;
  return false;
}

export function QuestionnaireView() {
  const router = useRouter();
  const [doc, setDoc] = useState<QuestionnaireDocument | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [answers, setAnswers] = useState<Record<string, AnswerValue>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const setAnswer = useCallback(
    (id: string, v: AnswerValue) => {
      setAnswers((prev) => {
        const next = { ...prev, [id]: v };

        if (id === "q1-degree-country") {
          const country = typeof v === "string" ? v.trim() : "";
          if (!country) {
            delete next["q1b-degree-type"];
            return next;
          }
          const allowed = doc?.degreesByCountry[country];
          const degreeType = next["q1b-degree-type"];
          if (
            allowed?.length &&
            typeof degreeType === "string" &&
            degreeType &&
            !allowed.includes(degreeType)
          ) {
            next["q1b-degree-type"] = "";
          }
          return next;
        }

        if (id === "q1b-degree-type") {
          const countryRaw = next["q1-degree-country"];
          const country = typeof countryRaw === "string" ? countryRaw.trim() : "";
          const allowed = country ? doc?.degreesByCountry[country] : undefined;
          if (allowed?.length && typeof v === "string" && v && !allowed.includes(v)) {
            next["q1b-degree-type"] = "";
          }
        }

        return next;
      });
    },
    [doc],
  );

  useEffect(() => {
    let cancelled = false;
    fetchQuestionnaire()
      .then((d) => {
        if (!cancelled) setDoc(d);
      })
      .catch(() => {
        if (!cancelled) setLoadError("Could not load questionnaire.");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const total = doc?.questions.length ?? 0;
  const filled = useMemo(() => {
    if (!doc) return 0;
    return doc.questions.filter((q) => isAnswerComplete(q, answers[q.id], answers)).length;
  }, [doc, answers]);
  const progressPct = total > 0 ? Math.round((filled / total) * 100) : 0;
  const formComplete = total > 0 && filled === total;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formComplete || submitting) return;
    setSubmitError(null);
    setSubmitting(true);
    const handoffId = crypto.randomUUID();
    try {
      const payload = await submitAnalysis({ answers });
      try {
        sessionStorage.setItem(analysisHandoffStorageKey(handoffId), JSON.stringify(payload));
      } catch {
        /* quota — SESSION_KEY in storeAnalysisResult may still succeed */
      }
      storeAnalysisResult(payload);
      router.push(`/analysis?h=${encodeURIComponent(handoffId)}`);
    } catch (err) {
      setSubmitting(false);
      const message =
        err instanceof Error ? err.message : "Could not generate your analysis. Please try again.";
      setSubmitError(message);
    }
  };

  if (loadError) {
    return (
      <div className="relative isolate flex min-h-dvh w-full flex-col items-center justify-center bg-slate-50 font-display text-slate-600">
        {loadError}
      </div>
    );
  }

  if (!doc) {
    return (
      <div className="relative isolate flex min-h-dvh w-full flex-col items-center justify-center bg-slate-50 font-display text-slate-500">
        Loading questionnaire…
      </div>
    );
  }

  return (
    <div className="relative isolate flex min-h-dvh w-full flex-col bg-[radial-gradient(129.64%_129.64%_at_-4116.67%_-4116.67%,rgba(125,211,252,0.15)_1.61%,rgba(125,211,252,0)_1.61%)] pb-px font-display text-dent-ink">
      <NavBar />
      <div
        className="sticky top-[68px] z-40 w-full border-b border-[#E2E8F0] bg-white/90 backdrop-blur-sm"
        role="presentation"
        aria-hidden
      >
        <div className="h-1 w-full bg-slate-100">
          <div
            className="h-full bg-sky-500 transition-[width] duration-200 ease-out"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      <main className="z-0 flex w-full flex-1 flex-col items-center self-stretch bg-slate-50 px-5 pb-12 pt-10 sm:pt-14">
        <form
          className="isolate flex w-full max-w-3xl flex-col items-start gap-4 rounded-3xl border border-sky-500/10 bg-white/90 p-7 shadow-[0_20px_25px_-5px_rgba(0,0,0,0.1),0_8px_10px_-6px_rgba(0,0,0,0.1)] backdrop-blur-sm"
          onSubmit={handleSubmit}
        >
          <div className="flex w-full max-w-full flex-col items-center pb-2">
            <h1 className="font-display mb-0.5 text-center text-[30px] font-extrabold leading-9 tracking-[-0.75px] text-[#0C1A3A]">
              {QUESTIONNAIRE_HEADING_TITLE}
            </h1>
            <p className="font-display mt-1 text-center text-[11px] font-medium leading-4 text-slate-500/80">
              {QUESTIONNAIRE_HEADING_SUBTITLE}
            </p>
          </div>

          {doc.questions.map((q) => (
            <QuestionnaireField
              key={q.id}
              doc={doc}
              question={q}
              value={answers[q.id]}
              answers={answers}
              onChange={setAnswer}
            />
          ))}

          <div className="flex w-full flex-col items-center gap-4 border-t border-slate-50 pt-4">
            {submitError ? (
              <p
                role="alert"
                className="w-full max-w-sm rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-center text-sm font-medium text-red-800"
              >
                {submitError}
              </p>
            ) : null}
            <div className="flex items-center gap-1.5 text-[10px] font-medium text-slate-400">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden>
                <path
                  d="M12 2C9.24 2 7 4.24 7 7V10C5.9 10 5 10.9 5 12V20C5 21.1 5.9 22 7 22H17C18.1 22 19 21.1 19 20V12C19 10.9 18.1 10 17 10V7C17 4.24 14.76 12 12 2Z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
                <path d="M12 16V16.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              Secure &amp; private assessment
            </div>
            <button
              type="submit"
              disabled={submitting || !formComplete}
              aria-busy={submitting}
              aria-disabled={submitting || !formComplete}
              title={!formComplete ? "Answer all questions to continue" : undefined}
              className={
                formComplete && !submitting
                  ? "flex h-12 w-full max-w-sm cursor-pointer items-center justify-center gap-2 rounded-full border-0 bg-sky-500 text-base font-extrabold text-white shadow-[0_10px_15px_-3px_rgba(14,165,233,0.2),0_4px_6px_-4px_rgba(14,165,233,0.2)] transition-all hover:bg-sky-600 active:scale-[0.98]"
                  : submitting
                    ? "pointer-events-none flex h-12 w-full max-w-sm cursor-wait items-center justify-center gap-2 rounded-full border-0 bg-sky-500 text-base font-extrabold text-white opacity-90 shadow-[0_10px_15px_-3px_rgba(14,165,233,0.2),0_4px_6px_-4px_rgba(14,165,233,0.2)] transition-all"
                    : "flex h-12 w-full max-w-sm cursor-not-allowed items-center justify-center gap-2 rounded-full border border-slate-300/40 bg-slate-50 text-base font-extrabold text-slate-400 shadow-none transition-all hover:bg-slate-50"
              }
            >
              {submitting ? (
                <svg
                  className="h-5 w-5 shrink-0 animate-spin text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  aria-hidden
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-90"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
              ) : null}
              <span>{submitting ? "Building your analysis…" : "See My Results"}</span>
            </button>
          </div>
        </form>

        <div className="mt-0 flex w-full max-w-3xl flex-col items-center gap-5 border-t border-[#eef2f6] pt-6">
          <p className="w-full max-w-[640px] text-center text-xs font-medium leading-relaxed text-slate-500">
            We use your answers only to tailor guidance for your U.S. dental pathway — not for marketing lists, and
            never sold to third parties.
          </p>
          <div className="flex w-full max-w-3xl flex-wrap items-center justify-center gap-4 pt-2">
            <div className="flex min-w-0 max-w-[200px] flex-1 flex-col items-center gap-0.5">
              <svg className="h-5 w-5 shrink-0 text-sky-500" viewBox="0 0 24 24" fill="none" aria-hidden>
                <path
                  d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <span className="text-center text-[11px] font-bold leading-snug text-[#0C1A3A]">Privacy-first</span>
            </div>
            <div className="flex min-w-0 max-w-[200px] flex-1 flex-col items-center gap-0.5">
              <svg className="h-5 w-5 shrink-0 text-sky-500" viewBox="0 0 24 24" fill="none" aria-hidden>
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5" />
                <path
                  d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10M12 2a15.3 15.3 0 00-4 10 15.3 15.3 0 004 10"
                  stroke="currentColor"
                  strokeWidth="1.5"
                />
              </svg>
              <span className="text-center text-[11px] font-bold leading-snug text-[#0C1A3A]">
                International dentists
              </span>
            </div>
            <div className="flex min-w-0 max-w-[200px] flex-1 flex-col items-center gap-0.5">
              <svg className="h-5 w-5 shrink-0 text-sky-500" viewBox="0 0 24 24" fill="none" aria-hidden>
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5" />
                <path
                  d="m16.24 7.76-2.04 6.12-6.12 2.04 2.04-6.12 6.12-2.04z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinejoin="round"
                />
              </svg>
              <span className="text-center text-[11px] font-bold leading-snug text-[#0C1A3A]">
                Navigate with clarity
              </span>
            </div>
          </div>
        </div>
      </main>

      <footer className="mt-12 flex w-full flex-col border-t border-slate-100 bg-white">
        <div className="mx-auto flex w-full max-w-[1440px] flex-row items-center justify-between px-6 py-4">
          <div className="text-sm font-bold text-slate-900">DentNav</div>
          <div className="flex gap-4">
            <Link href="#" className="text-[11px] text-slate-500 no-underline hover:text-slate-700">
              Privacy
            </Link>
            <Link href="#" className="text-[11px] text-slate-500 no-underline hover:text-slate-700">
              Terms
            </Link>
            <Link href="#" className="text-[11px] text-slate-500 no-underline hover:text-slate-700">
              Contact
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
