"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { createAnalysisAccessOrder, fetchAnalysisAccessPrice, verifyAnalysisAccessPayment } from "@/lib/api/booking";

// ─── Props ────────────────────────────────────────────────────────────────────

type AnalysisAccessModalProps = {
  onClose: () => void;
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

function loadRazorpayScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (document.getElementById("rzp-script")) { resolve(); return; }
    const script = document.createElement("script");
    script.id = "rzp-script";
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Failed to load Razorpay"));
    document.body.appendChild(script);
  });
}

function formatPrice(amount: number, currency: string) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: currency.toUpperCase(),
    minimumFractionDigits: 0,
  }).format(amount / 100);
}

// ─── Component ────────────────────────────────────────────────────────────────

type Phase = "ready" | "creating" | "paying" | "verifying" | "error";

export function AnalysisAccessModal({ onClose }: AnalysisAccessModalProps) {
  const router = useRouter();
  const paying = useRef(false);

  const [phase, setPhase] = useState<Phase>("ready");
  const [order, setOrder] = useState<{ orderId: string; amount: number; currency: string } | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [price, setPrice] = useState<{ amount: number; currency: string } | null>(null);

  const displayAmount = order?.amount ?? price?.amount ?? 0;
  const displayCurrency = order?.currency ?? price?.currency ?? "INR";
  const priceReady = displayAmount > 0;

  useEffect(() => {
    const serviceKey = process.env.NEXT_PUBLIC_SERVICE_KEY_ANALYSIS_ACCESS ?? "analysis_access";
    fetchAnalysisAccessPrice(serviceKey)
      .then((p) => setPrice(p))
      .catch(() => { /* price shown after order is created */ });
  }, []);

  const handleClose = useCallback(() => onClose(), [onClose]);

  // Keyboard close + scroll lock
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") handleClose(); };
    document.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [handleClose]);

  async function handlePay() {
    if (paying.current) return;
    paying.current = true;

    let activeOrder = order;
    if (!activeOrder) {
      setPhase("creating");
      try {
        const res = await createAnalysisAccessOrder();
        activeOrder = { orderId: res.order_id, amount: res.amount, currency: res.currency };
        setOrder(activeOrder);
      } catch (err: unknown) {
        paying.current = false;
        if (err instanceof Error && err.message === "already_paid") {
          // Already paid — refresh auth status and close
          router.replace("/landing?analysis_unlocked=1");
          onClose();
        } else {
          setErrorMsg("Could not create payment order. Please try again.");
          setPhase("error");
        }
        return;
      }
    }

    try {
      await loadRazorpayScript();
    } catch {
      paying.current = false;
      setErrorMsg("Could not load payment gateway. Please refresh and try again.");
      setPhase("error");
      return;
    }

    const key = process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID;
    if (!key) {
      paying.current = false;
      setErrorMsg("Payment gateway is not configured.");
      setPhase("error");
      return;
    }

    setPhase("paying");

    const rzp = new window.Razorpay({
      key,
      amount: activeOrder.amount,
      currency: activeOrder.currency.toUpperCase(),
      order_id: activeOrder.orderId,
      name: "DentNav",
      description: "Pathway Analysis — Lifetime Access",
      handler: async (response) => {
        setPhase("verifying");
        try {
          await verifyAnalysisAccessPayment(
            response.razorpay_order_id,
            response.razorpay_payment_id,
            response.razorpay_signature,
          );
          router.replace("/landing?analysis_unlocked=1");
          onClose();
        } catch {
          setErrorMsg("Payment could not be verified. If you were charged, please contact support.");
          setPhase("error");
        }
      },
      modal: {
        ondismiss: () => {
          paying.current = false;
          setPhase("ready");
        },
      },
      theme: { color: "#0C1A2E" },
    });

    rzp.open();
  }

  const isBusy = phase === "creating" || phase === "paying" || phase === "verifying";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={handleClose}
        aria-hidden
      />

      {/* Modal */}
      <div className="relative z-10 flex w-full max-w-2xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl sm:flex-row">

        {/* Close */}
        <button
          type="button"
          onClick={handleClose}
          aria-label="Close"
          className="absolute right-3 top-3 z-20 flex h-7 w-7 items-center justify-center rounded-full bg-white/90 text-[#64748B] shadow-sm transition-colors hover:bg-slate-100 hover:text-dent-ink"
        >
          <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5" aria-hidden>
            <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>

        {/* ── Left: what you get ────────────────────────────────────────── */}
        <div className="flex flex-col gap-4 border-b border-[#F1F5F9] p-5 sm:w-[55%] sm:border-b-0 sm:border-r sm:p-6">

          {/* Badge + title */}
          <div>
            <div className="inline-flex items-center gap-1.5 rounded-full border border-dent-sky/20 bg-dent-badge-bg px-2.5 py-1">
              <span className="h-1.5 w-1.5 rounded-full bg-dent-sky" aria-hidden />
              <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-dent-deep">One-time access</span>
            </div>
            <h2 className="mt-3 font-display text-lg font-bold leading-snug text-dent-ink">
              Unlock your personalised pathway analysis
            </h2>
            <p className="mt-1.5 text-[13px] leading-relaxed text-[#64748B]">
              Built entirely on your questionnaire responses — not a generic checklist.
            </p>
          </div>

          <div className="h-px bg-[#F1F5F9]" />

          {/* Inclusions */}
          <div>
            <p className="mb-3 text-[10px] font-bold uppercase tracking-[0.14em] text-[#94A3B8]">What&apos;s included</p>
            <div className="space-y-2.5">
              {[
                "Pathway tailored to your credentials and target states",
                "Exam sequencing with recommended order and timing",
                "Credential evaluation requirements for your background",
                "Notes on common bottlenecks and how to navigate them",
                "Revisit anytime as your situation evolves",
              ].map((label) => (
                <div key={label} className="flex items-start gap-2.5">
                  <div className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-emerald-50 ring-1 ring-emerald-100">
                    <svg viewBox="0 0 12 12" fill="none" className="h-2.5 w-2.5 text-emerald-500" aria-hidden>
                      <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                  <span className="text-[12px] leading-snug text-[#475569]">{label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Right: pricing + payment ──────────────────────────────────── */}
        <div className="flex flex-col justify-between p-5 sm:w-[45%] sm:p-6">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#94A3B8]">Order summary</p>
            <div className="mt-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[13px] text-[#64748B]">Pathway analysis</span>
                <span className="text-[13px] font-semibold text-dent-ink">
                  {priceReady ? formatPrice(displayAmount, displayCurrency) : "—"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[13px] text-[#64748B]">One-time, lifetime access</span>
                <span className="text-[12px] font-medium text-emerald-600">Permanent</span>
              </div>
              <div className="h-px bg-[#F1F5F9]" />
              <div className="flex items-center justify-between">
                <span className="text-[14px] font-bold text-dent-ink">Total due</span>
                <span className="font-display text-xl font-bold text-dent-ink">
                  {priceReady ? formatPrice(displayAmount, displayCurrency) : "—"}
                </span>
              </div>
            </div>
          </div>

          <div className="mt-6 flex flex-col gap-3">

            {/* Error */}
            {phase === "error" && errorMsg && (
              <div className="rounded-xl border border-red-100 bg-red-50 px-4 py-3">
                <p className="text-[12px] text-red-600">{errorMsg}</p>
              </div>
            )}

            {/* Pay button */}
            <button
              type="button"
              onClick={handlePay}
              disabled={isBusy}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-dent-ink py-3.5 text-[14px] font-semibold text-white transition-colors hover:bg-dent-deep disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isBusy ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  {phase === "creating" && "Preparing…"}
                  {phase === "paying" && "Opening payment…"}
                  {phase === "verifying" && "Verifying…"}
                </>
              ) : (
                <>
                  <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4" aria-hidden>
                    <rect x="1" y="5" width="18" height="12" rx="2" stroke="currentColor" strokeWidth="1.5" />
                    <path d="M1 9h18" stroke="currentColor" strokeWidth="1.5" />
                  </svg>
                  {phase === "error" ? "Try again" : priceReady ? `Pay ${formatPrice(displayAmount, displayCurrency)}` : "Pay now"}
                </>
              )}
            </button>

            {/* Trust */}
            <div className="flex items-center justify-center gap-1.5 text-[11px] text-[#94A3B8]">
              <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5" aria-hidden>
                <path d="M8 1.5L2 4v4c0 3.31 2.57 6.41 6 7 3.43-.59 6-3.69 6-7V4L8 1.5z" stroke="currentColor" strokeWidth="1.25" strokeLinejoin="round" />
                <path d="M5.5 8l1.5 1.5 3-3" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Secured by Razorpay · One-time payment · No subscription
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
