"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  {
    label: "Home",
    href: "/landing",
    inactiveClass:
      "text-dent-ink hover:bg-dent-badge-bg/60 hover:text-dent-ink",
    activeClass:
      "bg-dent-ink text-white shadow-[inset_0_0_0_1px_rgba(255,255,255,0.10)]",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-3.5 w-3.5 shrink-0" aria-hidden>
        <path
          d="M9 22V12h6v10M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  {
    label: "Packages",
    href: "/landing/packages",
    inactiveClass:
      "text-dent-ink hover:bg-dent-badge-bg/60 hover:text-dent-ink",
    activeClass:
      "bg-dent-ink text-white shadow-[inset_0_0_0_1px_rgba(255,255,255,0.10)]",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-3.5 w-3.5 shrink-0" aria-hidden>
        <path
          d="M16.5 9.4l-9-5.19M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M3.27 6.96L12 12.01l8.73-5.05M12 22.08V12"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
  },
  {
    label: "About",
    href: "/landing/about",
    inactiveClass:
      "text-dent-ink hover:bg-dent-badge-bg/60 hover:text-dent-ink",
    activeClass:
      "bg-dent-ink text-white shadow-[inset_0_0_0_1px_rgba(255,255,255,0.10)]",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-3.5 w-3.5 shrink-0" aria-hidden>
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <path d="M12 16v-4M12 8h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    ),
  },
] as const;

export function LandingSidebar() {
  const pathname = usePathname();

  return (
    <aside
      aria-label="Workspace navigation"
      className="fixed left-(--landing-outset) z-40 w-(--landing-sidebar-w) overflow-hidden rounded-2xl border border-[#E2E8F0] bg-white/95 p-1 shadow-[0_8px_24px_-12px_rgba(15,23,42,0.12)] backdrop-blur-sm supports-backdrop-filter:bg-white/90"
      style={{ top: "calc(var(--landing-header-h) + var(--landing-sidebar-gap))" }}
    >
      <nav className="flex flex-col gap-0.5">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-xs font-bold transition-colors duration-200 outline-none focus-visible:ring-2 focus-visible:ring-dent-sky focus-visible:ring-offset-1 ${
                isActive ? item.activeClass : item.inactiveClass
              }`}
            >
              <span className={isActive ? "opacity-90" : "opacity-70"}>{item.icon}</span>
              <span className="truncate tracking-wide">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
