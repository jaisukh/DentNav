"use client";

import { BrandLogo } from "@/components/home/BrandLogo";
import Link from "next/link";

export function LandingHeader() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-[#E2E8F0] bg-white/80 shadow-[0_1px_2px_rgba(0,0,0,0.05)] backdrop-blur-md supports-[backdrop-filter]:bg-white/80">
      <div className="page-shell flex h-[var(--landing-header-h)] items-center justify-between gap-4">
        <BrandLogo href="/landing" compact iconSize={32} />

        <nav className="flex items-center gap-1 sm:gap-2" aria-label="Account">
          <button
            className="shrink-0 rounded-xl px-3 py-2 text-sm font-medium text-[#3E4850] transition-colors duration-200 hover:bg-slate-50 hover:text-dent-ink"
          >
            Contact Us
          </button>
          <Link
            href="/"
            className="shrink-0 rounded-xl px-3 py-2 text-sm font-medium text-[#3E4850] transition-colors duration-200 hover:bg-slate-50 hover:text-dent-ink"
          >
            Sign out
          </Link>
        </nav>
      </div>
    </header>
  );
}
