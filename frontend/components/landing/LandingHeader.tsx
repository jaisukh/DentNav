"use client";

import { signOut } from "@/lib/api/auth";
import { BrandLogo } from "@/components/home/BrandLogo";
import { useRouter } from "next/navigation";
import { useAuthStatus } from "@/lib/auth-status-context";

export function LandingHeader() {
  const router = useRouter();
  const { clear } = useAuthStatus();

  async function handleSignOut() {
    // Tell the backend to clear the session cookie, then immediately wipe
    // the in-memory auth cache so the marketing page we're navigating to
    // doesn't read a stale `signedIn: true` from the previous session.
    // (The AuthStatusProvider lives in the root layout — it does not
    // remount on client-side navigation, so without `clear()` the next
    // render would still see the old session and pop the
    // "You're already signed in" modal on every Sign-In button.)
    await signOut();
    clear();
    router.push("/");
    router.refresh();
  }

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
          <button
            type="button"
            onClick={handleSignOut}
            className="shrink-0 rounded-xl px-3 py-2 text-sm font-medium text-[#3E4850] transition-colors duration-200 hover:bg-slate-50 hover:text-dent-ink"
          >
            Sign out
          </button>
        </nav>
      </div>
    </header>
  );
}
