import { Footer } from "@/components/home/Footer";
import { NavBar } from "@/components/home/NavBar";
import { AboutPageContent } from "@/components/about/AboutPageContent";

export default function AboutPage() {
  return (
    <div className="flex min-h-full flex-col bg-sky-50 text-dent-ink">
      <NavBar />
      <main className="flex-1">
        <AboutPageContent />
      </main>
      <Footer />
    </div>
  );
}
