import Link from "next/link";
import { LandingPromptCard } from "@/components/landing/LandingPromptCard";

/**
 * Shown when the user completed the questionnaire AND has paid.
 */
export function ViewAnalysis() {
  return (
    <LandingPromptCard
      eyebrow="All set"
      eyebrowClassName="text-dent-deep"
      title="Your pathway analysis is ready"
      description="Open your personalised roadmap anytime. You’ll find exam sequencing, documentation notes, and suggested milestones — organised so you can share with mentors or advisors or work through it on your own."
      featuresTitle="Inside your analysis"
      features={[
        "Roadmap tailored to your credentials and target states",
        "Notes on common bottlenecks and how to avoid them",
        "Export-friendly structure for your records (coming soon)",
      ]}
      gradientClassName="bg-linear-to-br from-white via-dent-badge-bg/40 to-white"
      iconBadgeClassName="bg-sky-50 text-dent-deep ring-sky-100"
      icon={
        <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" aria-hidden>
          <path
            d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      }
    >
      <Link
        href="/analysis"
        className="group inline-flex items-center gap-2.5 rounded-full border border-[#E2E8F0] bg-white px-8 py-3.5 text-sm font-bold text-dent-ink shadow-[0_1px_2px_rgba(0,0,0,0.05)] transition-all duration-200 hover:border-dent-sky/40 hover:bg-dent-badge-bg/50 active:scale-[0.98]"
      >
        <span>Open your analysis</span>
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
