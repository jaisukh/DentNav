import { QuestionnaireLink } from "@/components/questionnaire/QuestionnaireLink";
import { LandingPromptCard } from "@/components/landing/LandingPromptCard";

/**
 * Shown when the user has NOT yet completed the questionnaire.
 */
export function QuestionnairePrompt() {
  return (
    <LandingPromptCard
      eyebrow="Getting started"
      eyebrowClassName="text-dent-deep"
      title="Tell us about your background"
      description="Answer a focused questionnaire so we can map the exams, state requirements, and timeline that actually apply to you — not a generic checklist. It takes most people about ten to fifteen minutes."
      featuresTitle="After you submit"
      features={[
        "We match your credentials and goals to U.S. licensing pathways",
        "You’ll see which exams and documents typically come next for your case",
        "Your answers power the personalised analysis unlocked with a package",
      ]}
      gradientClassName="bg-linear-to-br from-white via-white to-dent-badge-bg/45"
      iconBadgeClassName="bg-sky-50 text-dent-deep ring-sky-100"
      icon={
        <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" aria-hidden>
          <path
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path d="M12 12v4M12 8h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
      }
    >
      <QuestionnaireLink
        className="group inline-flex items-center gap-2.5 rounded-full border border-[#E2E8F0] bg-white px-8 py-3.5 text-sm font-bold text-dent-ink shadow-[0_1px_2px_rgba(0,0,0,0.05)] transition-all duration-200 hover:border-dent-sky/40 hover:bg-dent-badge-bg/50 active:scale-[0.98]"
      >
        <span>Start questionnaire</span>
        <svg
          viewBox="0 0 16 16"
          fill="none"
          className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5"
          aria-hidden
        >
          <path d="M3.33 8h9.34M8.67 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </QuestionnaireLink>
    </LandingPromptCard>
  );
}
