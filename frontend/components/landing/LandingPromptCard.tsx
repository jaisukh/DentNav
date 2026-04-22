import type { ReactNode } from "react";

export type LandingPromptCardProps = {
  eyebrow: string;
  eyebrowClassName: string;
  title: string;
  description: string;
  featuresTitle?: string;
  features: string[];
  gradientClassName: string;
  iconBadgeClassName: string;
  icon: ReactNode;
  children: ReactNode;
};

export function LandingPromptCard({
  eyebrow,
  eyebrowClassName,
  title,
  description,
  featuresTitle = "What you'll get",
  features,
  gradientClassName,
  iconBadgeClassName,
  icon,
  children,
}: LandingPromptCardProps) {
  return (
    <div className="w-full overflow-hidden rounded-2xl border border-[#E2E8F0] bg-white shadow-[0_8px_32px_-12px_rgba(13,28,46,0.12)]">
      <div className={`grid lg:grid-cols-[1fr_minmax(0,22rem)] ${gradientClassName}`}>

        {/* Left — headline + CTA */}
        <div className="flex flex-col justify-between px-6 py-7 sm:px-8 sm:py-8">
          <div>
            <div className="flex items-center gap-3">
              <span
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-xl ring-1 ${iconBadgeClassName}`}
                aria-hidden
              >
                {icon}
              </span>
              <p className={`text-[11px] font-bold uppercase tracking-[0.2em] ${eyebrowClassName}`}>{eyebrow}</p>
            </div>

            <h2 className="mt-3 font-display text-xl font-bold tracking-tight text-dent-ink sm:text-2xl lg:leading-tight">
              {title}
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-[#64748B]">{description}</p>
          </div>

          <div className="mt-5">{children}</div>
        </div>

        {/* Right — feature list */}
        <div className="flex flex-col justify-center border-t border-[#E2E8F0] bg-[#F8FAFC]/70 px-6 py-7 sm:px-8 lg:border-l lg:border-t-0">
          <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-[#94A3B8]">{featuresTitle}</p>
          <ul className="mt-4 space-y-3">
            {features.map((line) => (
              <li key={line} className="flex gap-3 text-sm leading-snug text-[#475569]">
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-dent-badge-bg text-dent-deep ring-1 ring-dent-sky/15">
                  <svg viewBox="0 0 12 12" fill="none" className="h-2.5 w-2.5" aria-hidden>
                    <path
                      d="M2.5 6L5 8.5L9.5 3.5"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>
                <span>{line}</span>
              </li>
            ))}
          </ul>
        </div>

      </div>
    </div>
  );
}
