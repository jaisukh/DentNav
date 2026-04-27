import { SignInLink } from "@/components/auth/SignInLink";

function TimelineRow() {
  return (
    <div className="relative px-5 sm:px-20">
      <div className="absolute left-5 right-5 top-8 h-0.5 bg-slate-200 sm:left-20 sm:right-20" />
      <div className="relative flex justify-between">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="flex w-24 flex-col items-center gap-4">
            <div className="h-16 w-16 rounded-full bg-slate-300" />
            <div className="h-4 w-24 rounded-2xl bg-slate-200" />
          </div>
        ))}
      </div>
    </div>
  );
}

function RoadmapSkeleton() {
  return (
    <div className="flex w-full flex-col gap-16">
      {/* Timeline */}
      <div className="flex flex-col gap-12">
        <h2 className="font-display text-center text-[30px] font-bold leading-9 text-slate-900">
          Your U.S. dentistry roadmap
        </h2>
        <TimelineRow />
      </div>

      {/* Program Cards */}
      <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
        {[0, 1, 2].map((i) => (
          <div key={i} className="h-64 rounded-[32px] bg-slate-100" />
        ))}
      </div>

      {/* Checklist */}
      <div className="rounded-[32px] bg-slate-50 p-12">
        <div className="flex flex-col gap-6">
          <div className="h-6 w-80 rounded-2xl bg-slate-200" />
          <div className="h-4 w-full rounded-2xl bg-slate-200" />
          <div className="h-4 w-full rounded-2xl bg-slate-200" />
          <div className="h-4 w-2/3 rounded-2xl bg-slate-200" />
        </div>
      </div>
    </div>
  );
}

export function BlurredRoadmapSection() {
  return (
    <section className="relative isolate w-full overflow-hidden bg-white px-6 pb-10 pt-20 lg:px-[95px]">
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(70.71%_70.71%_at_50%_50%,#0EA5E9_2.95%,rgba(14,165,233,0)_2.95%),#FFFFFF] opacity-[0.05]"
        aria-hidden
      />

      <div className="relative mx-auto min-h-[700px] w-full max-w-[1280px] py-4">
        {/* Blurred skeleton content */}
        <div className="opacity-30 blur-[7px]" aria-hidden>
          <RoadmapSkeleton />
        </div>

        {/* Lock overlay — centered card on top of blur */}
        <div className="pointer-events-none absolute inset-0 z-10 flex items-start justify-center bg-white/80 px-4 pt-6 backdrop-blur-[2px]">
          <div className="pointer-events-auto w-full max-w-[512px] rounded-[32px] border border-sky-500/10 bg-white/[0.98] shadow-[0_25px_50px_-12px_rgba(0,0,0,0.25)] backdrop-blur-xl">
            {/* Inner card content with absolute-like spacing matching Figma */}
            <div className="flex flex-col items-center px-10 pb-10 pt-10">
              {/* Lock icon circle */}
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-sky-500/20">
                <svg width="24" height="32" viewBox="0 0 24 28" fill="none" aria-hidden>
                  <path
                    d="M18 10h-1V7c0-2.76-2.24-5-5-5S7 4.24 7 7v3H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V12c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3-9H9V7c0-1.66 1.34-3 3-3s3 1.34 3 3v3z"
                    fill="#0EA5E9"
                  />
                </svg>
              </div>

              {/* Heading */}
              <h2 className="font-display mt-8 text-center text-[30px] font-extrabold leading-9 tracking-[-0.75px] text-slate-900">
                Unlock your full roadmap
              </h2>

              {/* Description */}
              <p className="font-display mt-4 max-w-[420px] text-center text-base font-medium leading-[26px] text-slate-600">
                See program timelines, exam checkpoints, and a personalized checklist aligned to your profile—available
                when you continue with DentNav.
              </p>

              {/* Primary CTA */}
              <SignInLink
                className="font-display mt-10 flex h-14 w-full items-center justify-center rounded-full bg-slate-900 text-base font-bold text-white transition-opacity hover:opacity-90"
              >
                Continue with Google
              </SignInLink>

              {/* Divider with "OR" */}
              <div className="mt-6 flex w-full items-center gap-4">
                <div className="h-px flex-1 bg-slate-200" />
                <span className="font-display text-xs font-bold uppercase tracking-[1.2px] text-slate-400">or</span>
                <div className="h-px flex-1 bg-slate-200" />
              </div>

              {/* Secondary CTA */}
              <SignInLink
                className="font-display mt-6 flex h-[60px] w-full items-center justify-center rounded-full border-2 border-slate-200 text-base font-bold text-slate-600 transition-colors hover:border-slate-300 hover:bg-slate-50"
              >
                Sign in
              </SignInLink>

              {/* Disclaimer */}
              <p className="font-display mt-8 text-center text-xs leading-4 text-slate-400">
                Full roadmap access is part of DentNav onboarding. Availability may vary by region.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
