import Link from "next/link";
import { AboutPageContent } from "@/components/about/AboutPageContent";

export default function LandingAboutPage() {
  return (
    <div className="-mx-1 sm:-mx-2 lg:-mx-3 overflow-hidden rounded-2xl bg-white shadow-[0_4px_24px_-8px_rgba(15,23,42,0.10)]">
      <AboutPageContent
        secondaryCta={
          <Link
            href="/landing/packages"
            className="inline-flex items-center justify-center rounded-full border border-[#BAE6FD] bg-white px-7 py-3 text-sm font-bold text-[#0C4A6E] transition-all hover:border-[#7DD3FC] hover:bg-[#F0F9FF]"
          >
            View packages
          </Link>
        }
      />
    </div>
  );
}
