"use client";

import { LandingFooter } from "@/components/landing/LandingFooter";
import { LandingSidebar } from "@/components/landing/LandingSidebar";

export function LandingContent({ children }: { children: React.ReactNode }) {
  return (
    <>
      <LandingSidebar />

      <div className="flex flex-1 flex-col pt-[calc(var(--landing-header-h)+var(--landing-sidebar-gap))]">
        <main
          className="flex-1 pr-(--landing-outset) pb-8"
          style={{
            paddingLeft: "calc(var(--landing-outset) + var(--landing-sidebar-w) + var(--landing-rail-gap))",
          }}
        >
          <div className="px-1 sm:px-2 lg:px-3">{children}</div>
        </main>

        <div className="relative z-10 mt-auto w-full max-w-none shrink-0">
          <LandingFooter />
        </div>
      </div>
    </>
  );
}
