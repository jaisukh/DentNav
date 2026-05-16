"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { createOrder, releaseSlot, verifyPayment } from "@/lib/api/booking";

// ─── Razorpay types ───────────────────────────────────────────────────────────

declare global {
  interface Window {
    Razorpay: new (options: RazorpayOptions) => RazorpayInstance;
  }
}

type RazorpayOptions = {
  key: string;
  amount: number;
  currency: string;
  order_id: string;
  name: string;
  description: string;
  handler: (response: RazorpaySuccessResponse) => void;
  modal: { ondismiss: () => void };
  prefill?: { name?: string; email?: string };
  theme?: { color?: string };
};

type RazorpaySuccessResponse = {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
};

type RazorpayInstance = { open: () => void };

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
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency.toUpperCase(),
    minimumFractionDigits: 0,
  }).format(amount / 100);
}

function formatSlotTime(iso: string) {
  const d = new Date(iso);
  return {
    date: d.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" }),
    time: d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true }),
  };
}

// ─── Countdown timer ──────────────────────────────────────────────────────────

function useCountdown(expiresAt: string | null) {
  const [secondsLeft, setSecondsLeft] = useState<number | null>(null);

  useEffect(() => {
    if (!expiresAt) return;
    const tick = () => {
      const diff = Math.max(0, Math.floor((new Date(expiresAt).getTime() - Date.now()) / 1000));
      setSecondsLeft(diff);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [expiresAt]);

  return secondsLeft;
}

// ─── Page ─────────────────────────────────────────────────────────────────────

// Phases before Pay is clicked use the 5-min reservation window.
// Once Pay is clicked, createOrder runs and Razorpay takes over timing.
type Phase = "ready" | "creating" | "paying" | "verifying" | "success" | "expired" | "error";

export default function CheckoutPage() {
  const params = useParams<{ serviceKey: string; doctorServiceId: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();

  const slotIso = searchParams.get("slot") ?? "";
  const doctorName = searchParams.get("name") ?? "Doctor";
  const reservationExpiresAt = searchParams.get("expires_at") ?? null;
  const reservationId = searchParams.get("reservation_id") ?? null;
  const { serviceKey, doctorServiceId } = params;

  const [phase, setPhase] = useState<Phase>("ready");
  const [order, setOrder] = useState<{ orderId: string; amount: number; currency: string; bookingId: string } | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const paying = useRef(false);
  const secondsLeft = useCountdown(reservationExpiresAt);

  // ── Expire when reservation countdown hits zero (only before order is created) ──
  // Once createOrder succeeds, the pending_payment booking holds the slot for
  // 10 min — the reservation countdown is no longer the gate.

  useEffect(() => {
    if (secondsLeft === 0 && phase === "ready" && !order) {
      setPhase("expired");
    }
  }, [secondsLeft, phase, order]);

  // ── Pay: create order then open Razorpay ──────────────────────────────────

  async function handlePay() {
    if (paying.current || !slotIso) return;
    paying.current = true;

    // Step 1 — create Razorpay order only once; reuse on Razorpay dismissal + retry
    let activeOrder = order;
    if (!activeOrder) {
      setPhase("creating");
      try {
        const res = await createOrder(doctorServiceId, slotIso);
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

    if (!activeOrder) return;

    // Step 2 — load Razorpay script
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
      description: `Session with ${doctorName}`,
      handler: async (response) => {
        setPhase("verifying");
        try {
          await verifyPayment(
            response.razorpay_order_id,
            response.razorpay_payment_id,
            response.razorpay_signature,
          );
          setPhase("success");
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
          // Don't cancel the booking — payment may still succeed via Razorpay webhook.
          // The slot_expires_at (10 min) will free the slot automatically if no payment arrives.
          router.push(`/landing/booking/${serviceKey}`);
        },
      },
      theme: { color: "#0C1A2E" },
    });

    rzp.open();
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  const slot = slotIso ? formatSlotTime(slotIso) : null;

  return (
    <div className="flex w-full max-w-lg flex-col pb-14">

      {/* Back */}
      {phase !== "success" && (
        <button
          type="button"
          onClick={async () => {
            if (!order && reservationId) {
              await releaseSlot(reservationId).catch(() => {});
            }
            router.push(`/landing/booking/${serviceKey}`);
          }}
          className="mb-8 inline-flex items-center gap-1.5 text-[13px] font-medium text-[#64748B] transition-colors hover:text-dent-ink"
        >
          <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5" aria-hidden>
            <path d="M12.67 8H3.33M7.33 4L3.33 8l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Back to doctors
        </button>
      )}

      {/* ── Success: redirect fires immediately; show brief spinner while navigating ── */}
      {phase === "success" && (
        <div className="flex items-center justify-center gap-2 py-16 text-[13px] text-[#94A3B8]">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#E2E8F0] border-t-dent-sky" />
          Booking confirmed — redirecting…
        </div>
      )}

      {/* ── Expired ── */}
      {phase === "expired" && (
        <div className="flex flex-col items-center gap-5 py-8 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-amber-50 ring-1 ring-amber-100">
            <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6 text-amber-500" aria-hidden>
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.75" />
              <path d="M12 7v5l3 3" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
            </svg>
          </div>
          <div>
            <h1 className="font-display text-xl font-bold text-dent-ink">Slot expired</h1>
            <p className="mt-2 text-[14px] text-[#64748B]">
              The hold on your slot has lapsed. Please go back and choose a new time.
            </p>
          </div>
          <Link
            href={`/landing/booking/${serviceKey}`}
            className="w-full rounded-xl bg-dent-ink py-3 text-center text-[13px] font-semibold text-white transition-colors hover:bg-dent-deep"
          >
            Choose another slot
          </Link>
        </div>
      )}

      {/* ── Error ── */}
      {phase === "error" && (
        <div className="flex flex-col items-center gap-5 py-8 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-50 ring-1 ring-red-100">
            <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6 text-red-500" aria-hidden>
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
          <div>
            <h1 className="font-display text-xl font-bold text-dent-ink">Something went wrong</h1>
            <p className="mt-2 text-[14px] text-[#64748B]">{errorMsg}</p>
          </div>
          <Link
            href={`/landing/booking/${serviceKey}`}
            className="w-full rounded-xl bg-dent-ink py-3 text-center text-[13px] font-semibold text-white transition-colors hover:bg-dent-deep"
          >
            Go back
          </Link>
        </div>
      )}

      {/* ── Ready / Creating / Paying / Verifying ── */}
      {(phase === "ready" || phase === "creating" || phase === "paying" || phase === "verifying") && (
        <>
          <header className="mb-8">
            <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#94A3B8]">
              Complete your booking
            </p>
            <h1 className="mt-1 font-display text-2xl font-bold tracking-tight text-dent-ink">
              Review &amp; pay
            </h1>
          </header>

          {/* Booking summary */}
          <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-sm">
            <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#94A3B8]">Booking details</p>

            <div className="mt-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[13px] text-[#64748B]">Doctor</span>
                <span className="text-[13px] font-semibold text-dent-ink">{doctorName}</span>
              </div>
              {slot && (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-[13px] text-[#64748B]">Date</span>
                    <span className="text-[13px] font-semibold text-dent-ink">{slot.date}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[13px] text-[#64748B]">Time</span>
                    <span className="text-[13px] font-semibold text-dent-ink">{slot.time}</span>
                  </div>
                </>
              )}
              {order && (
                <>
                  <div className="my-1 h-px bg-[#F1F5F9]" />
                  <div className="flex items-center justify-between">
                    <span className="text-[13px] font-semibold text-dent-ink">Total</span>
                    <span className="font-display text-base font-bold text-dent-ink">
                      {formatPrice(order.amount, order.currency)}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Reservation countdown — only before order is created */}
          {phase === "ready" && !order && secondsLeft !== null && secondsLeft > 0 && (
            <div className="mt-4 flex items-center gap-2 rounded-xl border border-amber-100 bg-amber-50 px-4 py-3">
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

          {/* CTA */}
          <div className="mt-5">
            {phase === "ready" && (
              <button
                type="button"
                onClick={handlePay}
                className="w-full rounded-xl bg-dent-ink py-3 text-[13px] font-semibold text-white transition-colors hover:bg-dent-deep"
              >
                Pay now
              </button>
            )}
            {phase === "creating" && (
              <div className="flex items-center justify-center gap-2 py-3 text-[13px] text-[#94A3B8]">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#E2E8F0] border-t-dent-sky" />
                Preparing payment…
              </div>
            )}
            {phase === "paying" && (
              <div className="flex items-center justify-center gap-2 py-3 text-[13px] text-[#94A3B8]">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#E2E8F0] border-t-dent-sky" />
                Opening payment…
              </div>
            )}
            {phase === "verifying" && (
              <div className="flex items-center justify-center gap-2 py-3 text-[13px] text-[#94A3B8]">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-[#E2E8F0] border-t-dent-sky" />
                Verifying payment…
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
