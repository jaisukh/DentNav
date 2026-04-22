import Link from "next/link";
import { LandingPromptCard } from "@/components/landing/LandingPromptCard";

/**
 * Shown when the user completed the questionnaire but has NOT paid.
 */
export function PaymentPrompt() {
  return (
    <LandingPromptCard
      eyebrow="Questionnaire complete"
      eyebrowClassName="text-dent-deep"
      title="Unlock your full pathway analysis"
      description="We’ve used your responses to build a tailored roadmap: recommended exams, sequencing, and practical next steps. Choose a package to open the full analysis and keep everything in one place."
      featuresTitle="Included with access"
      features={[
        "Personalised timeline based on your questionnaire answers",
        "Clear next actions for licensing and credential evaluation",
        "Guidance you can revisit as your situation changes",
      ]}
      gradientClassName="bg-linear-to-br from-white via-white to-emerald-50/35"
      iconBadgeClassName="bg-sky-50 text-dent-deep ring-sky-100"
      icon={
        <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" aria-hidden>
          <path d="M9 12l2 2 4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.75" />
        </svg>
      }
    >
      <Link
        href="/landing/packages"
        className="group inline-flex items-center gap-2.5 rounded-full bg-dent-ink px-8 py-3.5 text-sm font-bold text-white shadow-[0_1px_2px_rgba(0,0,0,0.05)] transition-all duration-200 hover:bg-dent-deep active:scale-[0.98]"
      >
        <span>View packages & pricing</span>
        <svg
          viewBox="0 0 16 16"
          fill="none"
          className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5"
          aria-hidden
        >
          <path d="M3.33 8h9.34M8.67 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </Link>
    </LandingPromptCard>
  );
}
