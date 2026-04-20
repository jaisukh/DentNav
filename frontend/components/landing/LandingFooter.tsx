import Link from "next/link";

/**
 * Single-line footer for /landing — keeps the fixed sidebar clearance small and avoids overlap on scroll.
 */
export function LandingFooter() {
  return (
    <footer className="border-t border-[#E2E8F0] bg-white/95 py-2.5 backdrop-blur-sm supports-[backdrop-filter]:bg-white/90">
      <div className="page-shell flex flex-wrap items-center justify-center gap-x-2 gap-y-1 px-4 text-[11px] leading-snug text-[#64748B] sm:text-xs sm:gap-x-3">
        <span>© {new Date().getFullYear()} DentNav. All rights reserved.</span>
        <span className="text-[#CBD5E1]" aria-hidden>
          ·
        </span>
      </div>
    </footer>
  );
}
