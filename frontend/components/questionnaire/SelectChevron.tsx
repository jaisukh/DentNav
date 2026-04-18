/** Chevron for native `<select>` when using `appearance-none`. */
export function SelectChevron() {
  return (
    <svg
      className="pointer-events-none absolute right-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-slate-500"
      viewBox="0 0 18 18"
      fill="none"
      aria-hidden
    >
      <path
        d="M4.5 7.5L9 12L13.5 7.5"
        stroke="currentColor"
        strokeWidth="1.35"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
