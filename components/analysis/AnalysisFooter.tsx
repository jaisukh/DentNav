import Link from "next/link";

const links = [
  { href: "#", label: "Privacy" },
  { href: "#", label: "Terms of Service" },
  { href: "#", label: "Cookie Policy" },
] as const;

export function AnalysisFooter() {
  return (
    <footer className="w-full border-t border-slate-200 bg-slate-50">
      <div className="mx-auto flex w-full max-w-[1440px] flex-col gap-8 px-8 py-12 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex max-w-md flex-col gap-2">
          <span className="font-display text-xl font-bold leading-7 text-slate-900">DentNav</span>
          <p className="font-display text-sm leading-5 text-slate-500">
            Clarity for international dentists building a career in the U.S.
          </p>
        </div>
        <nav className="flex flex-wrap items-center gap-x-8 gap-y-2">
          {links.map(({ href, label }) => (
            <Link
              key={label}
              href={href}
              className="font-display text-sm leading-5 text-slate-500 transition-colors hover:text-slate-800"
            >
              {label}
            </Link>
          ))}
        </nav>
      </div>
    </footer>
  );
}
