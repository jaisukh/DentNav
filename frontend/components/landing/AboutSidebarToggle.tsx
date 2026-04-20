"use client";

import { useSidebar } from "@/components/landing/SidebarContext";

export function AboutSidebarToggle() {
  const { open, toggle } = useSidebar();

  return (
    <button
      onClick={toggle}
      aria-label={open ? "Hide navigation" : "Show navigation"}
      title={open ? "Hide navigation" : "Show navigation"}
      className="fixed left-0 z-50 flex h-10 w-4 items-center justify-center rounded-r-md border border-l-0 border-[#E2E8F0] bg-white/90 text-[#94A3B8] shadow-sm backdrop-blur-sm transition-colors duration-200 hover:bg-white hover:text-dent-deep"
      style={{ top: "50vh", transform: "translateY(-50%)" }}
    >
      <svg viewBox="0 0 8 14" fill="none" className="h-3 w-1.5" aria-hidden>
        {open ? (
          /* Left-pointing chevron — sidebar is visible, click to hide */
          <path
            d="M7 1L1 7l6 6"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        ) : (
          /* Right-pointing chevron — sidebar is hidden, click to show */
          <path
            d="M1 1l6 6-6 6"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}
      </svg>
    </button>
  );
}
