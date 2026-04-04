import Link from "next/link";
import { BrandLogo } from "@/components/landing/BrandLogo";

export function AnalysisTopNav() {
  return (
    <header className="sticky top-0 z-[100] border-b border-slate-100/50 bg-white/90 shadow-[0_8px_32px_rgba(14,165,233,0.08)] backdrop-blur-[6px]">
      <div className="mx-auto flex h-[72px] w-full max-w-[1440px] items-center justify-between gap-4 px-6">
        <BrandLogo compact className="min-w-0 shrink-0" textClassName="font-bold text-[#0F172A]" />
        <nav className="flex shrink-0 items-center gap-4">
          <Link
            href="/auth/login"
            className="text-center text-base font-medium leading-6 text-slate-500 transition-colors hover:text-slate-700"
          >
            Sign In
          </Link>
          <Link
            href="/"
            className="relative isolate rounded-full bg-sky-500 px-6 py-2 text-base font-semibold leading-6 text-white shadow-[0_10px_15px_-3px_rgba(0,0,0,0.1),0_4px_6px_-4px_rgba(0,0,0,0.1)] transition-opacity hover:opacity-90"
          >
            Home
          </Link >
        </nav>
      </div>
      <div className="h-px w-full bg-slate-100/50" aria-hidden />
    </header>
  );
}
