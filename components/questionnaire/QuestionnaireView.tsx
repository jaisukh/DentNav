"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useMemo, useState } from "react";
import { BrandLogo } from "@/components/landing/BrandLogo";
import { getQuestionnaire } from "@/lib/questionnaire-loader";
import type { AnswerValue, Question } from "@/lib/questionnaire.types";
import { QuestionnaireField } from "./QuestionnaireField";

function isAnswerComplete(q: Question, val: AnswerValue | undefined): boolean {
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
  const doc = useMemo(() => getQuestionnaire(), []);
  const [answers, setAnswers] = useState<Record<string, AnswerValue>>({});

  const setAnswer = useCallback((id: string, v: AnswerValue) => {
    setAnswers((prev) => ({ ...prev, [id]: v }));
  }, []);

  const total = doc.questions.length;
  const filled = useMemo(
    () => doc.questions.filter((q) => isAnswerComplete(q, answers[q.id])).length,
    [doc.questions, answers],
  );
  const progressPct = total > 0 ? Math.round((filled / total) * 100) : 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    router.push("/analysis");
  };

  return (
    <div className="relative isolate z-0 mx-auto flex min-h-dvh w-full max-w-[1440px] flex-col items-start justify-between bg-[radial-gradient(129.64%_129.64%_at_-4116.67%_-4116.67%,rgba(125,211,252,0.15)_1.61%,rgba(125,211,252,0)_1.61%)] pb-px font-display">
      <nav
        className="fixed left-1/2 top-0 z-[100] flex w-full max-w-[1440px] -translate-x-1/2 flex-col items-start border-b border-slate-100 bg-white/95 backdrop-blur-[6px]"
        aria-label="Questionnaire"
      >
        <div className="flex h-[50px] w-full items-center justify-between px-7 py-2.5">
          <BrandLogo compact className="min-w-0 shrink-0" textClassName="font-bold text-[#1B3A5C]" />
          <div className="flex items-center gap-4">
            <Link
              href="/auth/login"
              className="text-xs font-semibold leading-[18px] text-slate-500 transition-colors hover:text-slate-700"
            >
              Logout
            </Link>
            <Link
              href="/"
              className="flex cursor-pointer flex-col items-center justify-center rounded-full bg-sky-500 px-4 py-1.5 text-xs font-bold leading-[18px] text-white no-underline transition-opacity hover:opacity-90"
            >
              Home
            </Link>
          </div>
        </div>
        <div className="absolute bottom-0 left-0 h-0.5 w-full bg-slate-100">
          <div
            className="h-full bg-sky-500 transition-[width] duration-200 ease-out"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </nav>

      <main className="z-0 mt-[51px] flex w-full flex-none flex-col items-center self-stretch bg-slate-50 px-5 pb-12 pt-16">
        <form
          className="isolate flex w-full max-w-3xl flex-col items-start gap-4 rounded-3xl border border-sky-500/10 bg-white/90 p-7 shadow-[0_20px_25px_-5px_rgba(0,0,0,0.1),0_8px_10px_-6px_rgba(0,0,0,0.1)] backdrop-blur-sm"
          onSubmit={handleSubmit}
        >
          <div className="flex w-full max-w-full flex-col items-center pb-2">
            <h1 className="font-display mb-0.5 text-center text-[30px] font-extrabold leading-9 tracking-[-0.75px] text-[#0C1A3A]">
              {doc.title}
            </h1>
            <p className="font-display mt-1 text-center text-[11px] font-medium leading-4 text-slate-500/80">
              {doc.subtitle}
            </p>
          </div>

          {doc.questions.map((q) => (
            <QuestionnaireField key={q.id} question={q} value={answers[q.id]} onChange={setAnswer} />
          ))}

          <div className="flex w-full flex-col items-center gap-4 border-t border-slate-50 pt-4">
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
              className="flex h-12 w-full max-w-sm cursor-pointer items-center justify-center rounded-full border-0 bg-sky-500 text-base font-extrabold text-white shadow-[0_10px_15px_-3px_rgba(14,165,233,0.2),0_4px_6px_-4px_rgba(14,165,233,0.2)] transition-all hover:bg-sky-600 active:scale-[0.98]"
            >
              See My Results
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
