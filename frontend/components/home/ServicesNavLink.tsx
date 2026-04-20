"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const linkClass =
  "text-center text-sm font-medium leading-5 text-[#3E4850] transition-colors hover:text-dent-ink";

export function ServicesNavLink() {
  const pathname = usePathname();

  return (
    <Link
      href="/#services"
      className={linkClass}
      onClick={(e) => {
        const onHome = pathname === "/";
        if (!onHome) return;

        e.preventDefault();
        document.getElementById("services")?.scrollIntoView({ behavior: "smooth", block: "start" });
        window.history.replaceState(null, "", "/#services");
      }}
    >
      Services
    </Link>
  );
}
