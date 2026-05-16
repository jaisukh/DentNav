"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { createOrder, releaseSlot, verifyPayment } from "@/lib/api/booking";
import type { DoctorForService } from "@/lib/api/booking";

// ─── Props ────────────────────────────────────────────────────────────────────

type CheckoutModalProps = {
  doctor: DoctorForService;
  serviceLabel: string;
  slot: string;
  reservationId: string;
  expiresAt: string;
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

function formatSlotTime(iso: string) {
  const d = new Date(iso);
  return {
    date: d.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" }),
    time: d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true }),
  };
}

function getInitials(name: string) {
  return name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase();
}

function useCountdown(expiresAt: string) {
  const [secondsLeft, setSecondsLeft] = useState<number>(() =>
    Math.max(0, Math.floor((new Date(expiresAt).getTime() - Date.now()) / 1000))
  );

  useEffect(() => {
    const tick = () => {
      setSecondsLeft(Math.max(0, Math.floor((new Date(expiresAt).getTime() - Date.now()) / 1000)));
    };
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [expiresAt]);

  return secondsLeft;
}

// ─── Component ────────────────────────────────────────────────────────────────

type Phase = "ready" | "creating" | "paying" | "verifying" | "expired" | "error";

export function CheckoutModal({
  doctor,
  serviceLabel,
  slot,
  reservationId,
  expiresAt,
  onClose,
}: CheckoutModalProps) {
  const router = useRouter();
  const paying = useRef(false);
  const secondsLeft = useCountdown(expiresAt);

  const [phase, setPhase] = useState<Phase>("ready");
  const [order, setOrder] = useState<{ orderId: string; amount: number; currency: string; bookingId: string } | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const displayAmount = order ? order.amount : doctor.effective_amount;
  const displayCurrency = order ? order.currency : doctor.currency;
  const slotFormatted = formatSlotTime(slot);

  // Mark expired when timer hits zero (and no order created yet)
  useEffect(() => {
    if (secondsLeft === 0 && phase === "ready" && !order) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setPhase("expired");
    }
  }, [secondsLeft, phase, order]);

  const handleClose = useCallback(async () => {
    if (!order) {
      await releaseSlot(reservationId).catch(() => {});
    }
    onClose();
  }, [order, reservationId, onClose]);

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
        const res = await createOrder(doctor.doctor_service_id, slot);
        activeOrder = { orderId: res.order_id, amount: res.amount, currency: res.currency, bookingId: res.booking_id };
        setOrder(activeOrder);
      } catch (err: unknown) {
        paying.current = false;
        if (err instanceof Error && err.message === "reservation_expired") {
          setPhase("expired");
        } else {
          setErrorMsg("Could not create payment order. Please go back and try again.");
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
      description: `Session with ${doctor.name}`,
      handler: async (response) => {
        setPhase("verifying");
        try {
          await verifyPayment(
            response.razorpay_order_id,
            response.razorpay_payment_id,
            response.razorpay_signature,
          );
          router.replace("/landing?booking_confirmed=1");
        } catch (err: unknown) {
          if (err instanceof Error && err.message === "slot_expired") {
            setPhase("expired");
          } else {
            setErrorMsg("Payment could not be verified. If you were charged, please contact support.");
            setPhase("error");
          }
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

  const isbusy = phase === "creating" || phase === "paying" || phase === "verifying";

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
          aria-label="Cancel and release slot"
          className="absolute right-3 top-3 z-20 flex h-7 w-7 items-center justify-center rounded-full bg-white/90 text-[#64748B] shadow-sm transition-colors hover:bg-slate-100 hover:text-dent-ink"
        >
          <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5" aria-hidden>
            <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </button>

        {/* ── Left: appointment summary ─────────────────────────────────────── */}
        <div className="flex flex-col gap-4 border-b border-[#F1F5F9] p-5 sm:w-[55%] sm:border-b-0 sm:border-r sm:p-6">

          {/* Doctor card */}
          <div className="flex items-center gap-3">
            {doctor.photo_url ? (
              <Image
                src={doctor.photo_url}
                alt={doctor.name}
                width={44}
                height={44}
                className="rounded-full object-cover ring-2 ring-[#F1F5F9]"
              />
            ) : (
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-dent-ink text-[13px] font-bold text-white">
                {getInitials(doctor.name)}
              </div>
            )}
            <div className="min-w-0">
              <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#94A3B8]">{serviceLabel}</p>
              <p className="truncate font-display text-[15px] font-bold text-dent-ink">{doctor.name}</p>
              {doctor.specializations.length > 0 && (
                <p className="mt-0.5 text-[12px] text-[#64748B]">{doctor.specializations[0]}</p>
              )}
            </div>
          </div>

          <div className="h-px bg-[#F1F5F9]" />

          {/* Appointment details */}
          <div>
            <p className="mb-3 text-[10px] font-bold uppercase tracking-[0.14em] text-[#94A3B8]">Appointment details</p>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-[#F8FAFF]">
                  <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5 text-dent-sky" aria-hidden>
                    <rect x="1" y="2" width="14" height="13" rx="1.5" stroke="currentColor" strokeWidth="1.25" />
                    <path d="M5 1v2M11 1v2M1 6h14" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" />
                  </svg>
                </div>
                <div>
                  <p className="text-[11px] font-medium text-[#94A3B8]">Date</p>
                  <p className="text-[13px] font-semibold text-dent-ink">{slotFormatted.date}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-[#F8FAFF]">
                  <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5 text-dent-sky" aria-hidden>
                    <circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.25" />
                    <path d="M8 5v3.5l2 2" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" />
                  </svg>
                </div>
                <div>
                  <p className="text-[11px] font-medium text-[#94A3B8]">Time</p>
                  <p className="text-[13px] font-semibold text-dent-ink">{slotFormatted.time}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="h-px bg-[#F1F5F9]" />

          {/* What's included */}
          <div>
            <p className="mb-3 text-[10px] font-bold uppercase tracking-[0.14em] text-[#94A3B8]">What&apos;s included</p>
            <div className="space-y-2.5">
              {[
                "Instant booking confirmation",
                "Confirmation email to both parties",
                "Calendar invite from your doctor",
              ].map((label) => (
                <div key={label} className="flex items-center gap-2">
                  <div className="flex h-4.5 w-4.5 shrink-0 items-center justify-center rounded-full bg-emerald-50">
                    <svg viewBox="0 0 12 12" fill="none" className="h-2.5 w-2.5 text-emerald-500" aria-hidden>
                      <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                  <span className="text-[12px] font-medium text-[#475569]">{label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Right: order summary + payment ───────────────────────────────── */}
        <div className="flex flex-col justify-between p-5 sm:w-[45%] sm:p-6">

          {/* Order summary */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#94A3B8]">Order summary</p>
            <div className="mt-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[13px] text-[#64748B]">Consultation</span>
                <span className="text-[13px] font-semibold text-dent-ink">
                  {formatPrice(displayAmount, displayCurrency)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[13px] text-[#64748B]">Platform fee</span>
                <span className="text-[13px] font-medium text-emerald-600">Free</span>
              </div>
              <div className="h-px bg-[#F1F5F9]" />
              <div className="flex items-center justify-between">
                <span className="text-[14px] font-bold text-dent-ink">Total due</span>
                <span className="font-display text-xl font-bold text-dent-ink">
                  {formatPrice(displayAmount, displayCurrency)}
                </span>
              </div>
            </div>
          </div>

          {/* CTA section */}
          <div className="mt-6 flex flex-col gap-3">

            {/* Expired */}
            {phase === "expired" && (
              <div className="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-center">
                <p className="text-[13px] font-semibold text-red-700">Slot expired</p>
                <p className="mt-0.5 text-[12px] text-red-600">Go back and choose a new time.</p>
              </div>
            )}

            {/* Error */}
            {phase === "error" && errorMsg && (
              <div className="rounded-xl border border-red-100 bg-red-50 px-4 py-3">
                <p className="text-[12px] text-red-600">{errorMsg}</p>
              </div>
            )}

            {/* Countdown */}
            {(phase === "ready" || isbusy) && secondsLeft > 0 && (
              <div className="flex items-center gap-2 rounded-xl border border-amber-100 bg-amber-50 px-3 py-2.5">
                <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4 shrink-0 text-amber-500" aria-hidden>
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.75" />
                  <path d="M12 7v5l3 3" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
                </svg>
                <p className="text-[12px] font-medium text-amber-700">
                  Slot held for{" "}
                  <span className="font-bold tabular-nums">
                    {String(Math.floor(secondsLeft / 60)).padStart(2, "0")}:
                    {String(secondsLeft % 60).padStart(2, "0")}
                  </span>
                </p>
              </div>
            )}

            {/* Pay button */}
            {phase !== "expired" && phase !== "error" && (
              <button
                type="button"
                onClick={handlePay}
                disabled={isbusy}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-dent-ink py-3.5 text-[14px] font-semibold text-white transition-colors hover:bg-dent-deep disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isbusy ? (
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
                    Pay {formatPrice(displayAmount, displayCurrency)}
                  </>
                )}
              </button>
            )}

            {/* Go back when error/expired */}
            {(phase === "expired" || phase === "error") && (
              <button
                type="button"
                onClick={handleClose}
                className="w-full rounded-xl border border-[#E2E8F0] bg-white py-3 text-[13px] font-semibold text-dent-ink transition-colors hover:bg-slate-50"
              >
                Choose another slot
              </button>
            )}

            {/* Trust line */}
            {phase !== "expired" && phase !== "error" && (
              <div className="flex items-center justify-center gap-1.5 text-[11px] text-[#94A3B8]">
                <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5" aria-hidden>
                  <path d="M8 1.5L2 4v4c0 3.31 2.57 6.41 6 7 3.43-.59 6-3.69 6-7V4L8 1.5z" stroke="currentColor" strokeWidth="1.25" strokeLinejoin="round" />
                  <path d="M5.5 8l1.5 1.5 3-3" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Secured by Razorpay · SSL encrypted
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
