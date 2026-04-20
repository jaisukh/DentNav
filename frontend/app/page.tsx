import { BentoSection } from "@/components/home/BentoSection";
import { CtaSection } from "@/components/home/CtaSection";
import { Footer } from "@/components/home/Footer";
import { HeroSection } from "@/components/home/HeroSection";
import { NavBar } from "@/components/home/NavBar";

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
