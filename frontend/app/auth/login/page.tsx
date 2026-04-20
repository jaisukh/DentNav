import Image from "next/image";
import Link from "next/link";
import iconMark from "@/app/icon.png";
import { AuthPanel } from "@/components/auth/AuthPanel";
import Particles from "@/components/auth/Particles";

export default function LoginPage() {
    return (
        <main className="flex h-[100dvh] max-h-[100dvh] w-full flex-col overflow-hidden bg-white lg:flex-row">
            {/* Left Panel — 55% width on desktop */}
            <section
                className="relative hidden h-full min-h-0 w-[55%] flex-col overflow-hidden lg:flex"
                style={{
                    background: "linear-gradient(145.49deg, #0EA5E9 0%, #0284C7 50%, #0C1A3A 100%)",
                }}
            >
                {/* WebGL particles — behind copy; hover via window listener so links stay clickable */}
                <div className="pointer-events-none absolute inset-0 z-[1] min-h-0">
                    <Particles
                        particleColors={["#ffffff"]}
                        particleCount={200}
                        particleSpread={10}
                        speed={0.1}
                        particleBaseSize={100}
                        moveParticlesOnHover
                        alphaParticles={false}
                        disableRotation={false}
                        pixelRatio={1}
                        className="h-full min-h-0 w-full"
                    />
                </div>

                {/* Background Decorative Elements */}
                <div className="pointer-events-none absolute inset-0 z-0" style={{
                    background: "radial-gradient(70.71% 70.71% at 50% 50%, rgba(255, 255, 255, 0.08) 4.42%, rgba(255, 255, 255, 0) 4.42%)"
                }} aria-hidden />

                {/* Decorative Circles */}
                <div className="absolute -left-[10%] -top-[10%] h-[50%] w-[50%] rounded-full border border-white/5" aria-hidden />
                <div className="absolute right-[-5%] bottom-[-5%] h-[40%] w-[45%] rounded-full border border-white/5" aria-hidden />

                <div className="relative z-10 flex min-h-0 flex-1 flex-col justify-between gap-4 p-6 lg:gap-5 lg:p-10">
                    {/* Header/Logo */}
                    <header className="shrink-0">
                        <Link
                            href="/"
                            className="inline-flex items-center gap-2.5"
                        >
                            <Image
                                src={iconMark}
                                alt=""
                                width={72}
                                height={72}
                                className="h-9 w-9 shrink-0 object-contain lg:h-10 lg:w-10"
                                priority
                            />
                            <span className="font-display text-2xl font-[800] leading-none tracking-[-1px] text-white lg:text-[26px]">
                                DentNav
                            </span>
                        </Link>
                    </header>

                    {/* Center Content */}
                    <div className="max-w-[576px] space-y-3 lg:space-y-4">
                        <div className="inline-flex items-center rounded-full bg-white/10 px-3 py-1 backdrop-blur-sm">
                            <span className="text-[9px] font-bold uppercase tracking-[1.5px] text-white">
                                Join the Community
                            </span>
                        </div>

                        <h1 className="font-display text-[28px] font-[800] leading-[1.12] tracking-[-0.8px] text-white lg:text-[34px] lg:leading-[1.08]">
                            Your U.S. Dental Career Starts Here
                        </h1>

                        <p className="text-sm font-medium leading-relaxed text-white/75 lg:text-[15px] lg:leading-6">
                            Access elite consulting resources, clinical roadmap tracking, and a premium network of dental professionals across the United States.
                        </p>
                    </div>

                    {/* Testimonial Glass Card */}
                    <div className="relative max-w-[500px] shrink-0 rounded-2xl border border-white/10 bg-white/12 p-4 shadow-[0_25px_50px_-12px_rgba(0,0,0,0.25)] backdrop-blur-[6px] lg:p-5">
                        <div className="flex items-center gap-3">
                            <div className="h-10 w-10 shrink-0 overflow-hidden rounded-full border-2 border-[#89CEFF] bg-slate-200">
                                <div className="flex h-full w-full items-center justify-center bg-dent-sky/20 text-xs font-bold uppercase text-dent-deep">
                                    KR
                                </div>
                            </div>
                            <div>
                                <h4 className="text-xs font-bold text-white lg:text-sm">Dr. Kumar Rudravaram</h4>
                                <div className="mt-0.5 flex gap-0.5">
                                    {[...Array(5)].map((_, i) => (
                                        <svg key={i} className="h-2 w-2 text-[#6BFF8F] lg:h-2.5 lg:w-2.5" fill="currentColor" viewBox="0 0 20 20" aria-hidden>
                                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                        </svg>
                                    ))}
                                </div>
                            </div>
                        </div>
                        <p className="mt-3 line-clamp-4 text-[12px] font-medium leading-[1.45] text-white/90 lg:mt-3.5 lg:text-[13px] lg:leading-[1.5]">
                            We know how overwhelming this journey can feel beacuse we&apos;ve lived it ourselves.
                            Today, through DentNav, our goal is simple: To make your journey clearer, smoother, and more achievable.
                            Remember,{" "}
                            <span className="font-bold">
                                &ldquo;You are capable, your dream is valid and is absolutely possible.&rdquo;
                            </span>
                        </p>
                    </div>
                </div>
            </section>

            {/* Right Panel — Google sign-in card */}
            <section className="relative flex h-full min-h-0 flex-1 flex-col overflow-hidden bg-gradient-to-b from-[#EFF6FF] via-white to-[#F1F5F9]">
                {/* Top Right Back Link */}
                <Link
                    href="/"
                    className="absolute right-5 top-5 z-10 flex items-center gap-1.5 text-xs font-semibold text-[#0EA5E9] transition-colors hover:text-[#0284C7] lg:right-8 lg:top-6 lg:text-sm"
                >
                    <svg className="h-2 w-2 rotate-180" viewBox="0 0 12 12" fill="none" aria-hidden>
                        <path d="M1 1L11 6L1 11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    Back to home
                </Link>

                <div className="flex min-h-0 flex-1 flex-col justify-center px-5 pb-5 pt-16 sm:px-8 sm:pb-6 sm:pt-20 lg:px-12 lg:pb-8 lg:pt-12">
                    <div className="mx-auto flex w-full max-w-[440px] flex-col items-center gap-2 sm:gap-2.5">
                        <div className="w-full rounded-[28px] border border-[#E2E8F0] bg-white/95 p-7 shadow-[0_24px_64px_-28px_rgba(12,26,58,0.22)] ring-1 ring-black/[0.03] backdrop-blur-[2px] sm:p-9 lg:p-10">
                            <div className="mb-7 flex justify-center lg:mb-8 lg:hidden">
                                <Link href="/" className="inline-flex items-center gap-2.5">
                                    <Image
                                        src={iconMark}
                                        alt=""
                                        width={72}
                                        height={72}
                                        className="h-10 w-10 shrink-0 object-contain"
                                        priority
                                    />
                                    <span className="font-display text-[22px] font-[800] leading-none tracking-[-0.5px] text-[#0C1A3A]">
                                        DentNav
                                    </span>
                                </Link>
                            </div>

                            <AuthPanel />

                            <div className="mt-8 flex flex-col gap-3 border-t border-[#EEF2F7] pt-7 lg:mt-10 lg:gap-3.5 lg:pt-8">
                                <p className="text-center text-[11px] font-semibold uppercase tracking-[0.85px] text-[#94A3B8]">
                                    Why Google?
                                </p>
                                <ul className="space-y-2.5 text-[13px] font-medium leading-snug text-[#475569] lg:text-[14px]">
                                    <li className="flex gap-2.5 rounded-xl bg-[#F8FAFC] px-3.5 py-3 lg:px-4 lg:py-3.5">
                                        <span className="shrink-0 text-[#0EA5E9]" aria-hidden>
                                            ✓
                                        </span>
                                        <span>No separate password — fewer credentials to manage</span>
                                    </li>
                                    <li className="flex gap-2.5 rounded-xl bg-[#F8FAFC] px-3.5 py-3 lg:px-4 lg:py-3.5">
                                        <span className="shrink-0 text-[#0EA5E9]" aria-hidden>
                                            ✓
                                        </span>
                                        <span>Industry-standard sign-in trusted worldwide</span>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <p className="text-center text-[10px] pt-4 font-bold uppercase tracking-[0.75px] text-[#64748B] lg:text-[11px]">
                            Authentication powered by Google
                        </p>
                    </div>
                </div>
            </section>
        </main>
    );
}
