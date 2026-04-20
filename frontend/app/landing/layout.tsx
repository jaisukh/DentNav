import { LandingHeader } from "@/components/landing/LandingHeader";
import { LandingContent } from "@/components/landing/LandingContent";

export default function LandingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div
      className="isolate flex min-h-dvh flex-col bg-[#F8F9FF] text-dent-ink [--landing-header-h:3.5rem] [--landing-outset:1rem] [--landing-rail-gap:2rem] [--landing-sidebar-gap:var(--landing-outset)] [--landing-sidebar-w:9rem] sm:[--landing-outset:1.25rem] sm:[--landing-sidebar-w:10rem]"
    >
      <LandingHeader />
      <LandingContent>{children}</LandingContent>
    </div>
  );
}
