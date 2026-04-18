import { BentoSection } from "@/components/landing/BentoSection";
import { CtaSection } from "@/components/landing/CtaSection";
import { Footer } from "@/components/landing/Footer";
import { HeroSection } from "@/components/landing/HeroSection";
import { NavBar } from "@/components/landing/NavBar";

export default function Home() {
  return (
    <div className="flex min-h-full flex-col bg-[#F8F9FF] text-dent-ink">
      <NavBar />
      <main className="flex-1">
        <HeroSection />
        <BentoSection />
        <CtaSection />
      </main>
      <Footer />
    </div>
  );
}
