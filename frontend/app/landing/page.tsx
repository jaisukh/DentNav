import { BrochureDownload } from "@/components/landing/BrochureDownload";
import { LandingVideoSection } from "@/components/landing/LandingVideoSection";
import { PaymentPrompt } from "@/components/landing/PaymentPrompt";
import { QuestionnairePrompt } from "@/components/landing/QuestionnairePrompt";
import { ViewAnalysis } from "@/components/landing/ViewAnalysis";

/*
 * ─── Feature flags ───────────────────────────────────────────────────
 * HAS_ANSWERED_QUESTIONNAIRE: false → questionnaire prompt
 * HAS_PAID: false → payment prompt, true → view analysis
 * TODO: Replace with a real API call.
 * ─────────────────────────────────────────────────────────────────────
 */
const HAS_ANSWERED_QUESTIONNAIRE = true;
const HAS_PAID = false;

export default function LandingPage() {
  return (
    <div className="w-full max-w-6xl pb-6">

      {/* ── Hero ─────────────────────────────────────────────────────── */}
      <header className="mb-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between lg:gap-6">
          <div className="min-w-0 max-w-3xl flex-1">
            <h1 className="font-display text-3xl font-bold tracking-tight text-dent-ink sm:text-4xl">
              Welcome back
            </h1>
            <p className="mt-2 text-sm leading-relaxed text-[#64748B] sm:text-base">
              Navigate U.S. dental licensing with a roadmap built entirely around your credentials, target states, and program type.
            </p>

            <div className="mt-4 grid gap-2 sm:grid-cols-3">
              {[
                { label: "Tailored",  body: "Guidance built on your answers" },
                { label: "Focused",   body: "Exams, docs, and sequencing" },
                { label: "One place", body: "Pick up anytime, on any device" },
              ].map(({ label, body }) => (
                <div key={label} className="rounded-xl border border-[#E2E8F0] bg-white/80 px-3 py-2.5 shadow-sm">
                  <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#94A3B8]">{label}</p>
                  <p className="mt-0.5 text-xs font-semibold leading-snug text-dent-ink">{body}</p>
                </div>
              ))}
            </div>

            <p className="mt-3 text-[11px] leading-relaxed text-[#64748B]">
              Your exam sequence, credential requirements, and all state-specific licensing rules — filtered to your profile, target states, and program type.
            </p>
            <p className="mt-1.5 text-[11px] leading-relaxed text-[#64748B]">
              Open your roadmap anytime on any device, revisit it as your plans evolve, or bring it to a 1:1 consultation for expert guidance.
            </p>

            <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1">
              <p className="text-sm font-bold text-shimmer">Mapped to your credentials.</p>
              <p className="text-sm font-bold text-shimmer" style={{ animationDelay: "1.3s" }}>Built for your timeline.</p>
              <p className="text-sm font-bold text-shimmer" style={{ animationDelay: "2.6s" }}>Yours to revisit, anytime.</p>
              <p className="text-sm font-bold text-shimmer" style={{ animationDelay: "3.9s" }}>Every state rule, decoded.</p>
            </div>
          </div>
          <BrochureDownload />
        </div>
      </header>

      {/* ── Prompt card ──────────────────────────────────────────────── */}
      <div className="w-full">
        {!HAS_ANSWERED_QUESTIONNAIRE ? (
          <QuestionnairePrompt />
        ) : !HAS_PAID ? (
          <PaymentPrompt />
        ) : (
          <ViewAnalysis />
        )}
      </div>

      <LandingVideoSection />
    </div>
  );
}
