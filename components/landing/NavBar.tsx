import { BrandLogo } from "./BrandLogo";
import Link from "next/link";

export function NavBar() {
  return (
    <header className="sticky top-0 z-50 border-b border-[#E2E8F0] bg-white/80 shadow-[0_1px_2px_rgba(0,0,0,0.05)] backdrop-blur-md supports-[backdrop-filter]:bg-white/80">
      <div className="page-shell flex h-[68px] items-center justify-between gap-2 sm:gap-2">
        <BrandLogo className="min-w-0 shrink-0" />
        <nav className="flex shrink-0 items-center gap-2 sm:gap-5">
          <Link
            href="/"
            className="text-center text-sm font-medium leading-5 text-[#3E4850] transition-colors hover:text-dent-ink"
          >
            Home
          </Link>
          <Link
            href="/about"
            className="text-center text-sm font-medium leading-5 text-[#3E4850] transition-colors hover:text-dent-ink"
          >
            About Us
          </Link>
          <Link
            href="/auth/login"
            className="text-center text-sm font-medium leading-5 text-[#3E4850] transition-colors hover:text-dent-ink"
          >
            Sign In
          </Link>
          <Link
            href="/questionnaire"
            className="rounded-full bg-dent-sky px-5 py-2.5 text-sm font-medium leading-5 text-white shadow-[0_1px_2px_rgba(0,0,0,0.05)] transition-opacity hover:opacity-90"
          >
            Get Started For Free
          </Link>
        </nav>
      </div>
    </header>
  );
}
